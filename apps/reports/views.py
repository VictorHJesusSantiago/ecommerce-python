from rest_framework import viewsets, status, permissions, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count, Avg, F
from django.utils import timezone
from datetime import timedelta

from .models import Report, AnalyticsEvent, DailyStats, ProductPerformance, SalesForecast
from .serializers import (
    ReportSerializer, ReportCreateSerializer, AnalyticsEventSerializer,
    DailyStatsSerializer, ProductPerformanceSerializer, SalesForecastSerializer,
    DashboardSerializer
)
from apps.common.permissions import IsAdminUser, CanManageReports
from apps.common.pagination import StandardResultsSetPagination


class ReportViewSet(viewsets.ModelViewSet):
    serializer_class = ReportSerializer
    permission_classes = [IsAdminUser]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        qs = Report.objects.all()
        report_type = self.request.query_params.get('type')
        if report_type:
            qs = qs.filter(report_type=report_type)
        return qs

    def get_serializer_class(self):
        if self.action == 'create':
            return ReportCreateSerializer
        return ReportSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from apps.common.utils import generate_unique_code
        report = Report.objects.create(
            name=serializer.validated_data['name'],
            report_type=serializer.validated_data['report_type'],
            date_from=serializer.validated_data.get('date_from'),
            date_to=serializer.validated_data.get('date_to'),
            filters=serializer.validated_data.get('filters', {}),
            generated_by=request.user,
            status='pending',
        )

        from .tasks import generate_report
        generate_report.delay(str(report.id))

        return Response({
            'success': True,
            'message': 'Report is being generated.',
            'report': ReportSerializer(report).data,
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        report = self.get_object()
        if report.status != 'completed':
            return Response({
                'success': False,
                'error': {'message': 'Report is not ready yet.'}
            }, status=400)
        if report.file:
            from django.http import FileResponse
            return FileResponse(report.file.open(), as_attachment=True, filename=f"{report.name}.csv")
        return Response({'success': True, 'data': report.data})


class AnalyticsEventViewSet(viewsets.ModelViewSet):
    serializer_class = AnalyticsEventSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        if self.request.user.is_staff:
            return AnalyticsEvent.objects.all()
        return AnalyticsEvent.objects.none()

    def perform_create(self, serializer):
        kwargs = {
            'user': self.request.user if self.request.user.is_authenticated else None,
            'session_key': self.request.session.session_key or '',
            'ip_address': self.request.META.get('REMOTE_ADDR'),
            'user_agent': self.request.META.get('HTTP_USER_AGENT', ''),
            'referrer': self.request.META.get('HTTP_REFERER', ''),
        }
        serializer.save(**kwargs)


class DailyStatsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DailyStatsSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        qs = DailyStats.objects.all()
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)
        return qs


class ProductPerformanceViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductPerformanceSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        qs = ProductPerformance.objects.select_related('product')
        product = self.request.query_params.get('product')
        if product:
            qs = qs.filter(product_id=product)
        return qs


class SalesForecastViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SalesForecastSerializer
    permission_classes = [IsAdminUser]
    queryset = SalesForecast.objects.all()


class DashboardView(generics.GenericAPIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        from apps.orders.models import Order
        from apps.products.models import Product
        from apps.users.models import User

        today = timezone.now().date()
        thirty_days_ago = today - timedelta(days=30)
        sixty_days_ago = today - timedelta(days=60)

        current_orders = Order.objects.filter(created_at__date__gte=thirty_days_ago)
        previous_orders = Order.objects.filter(
            created_at__date__gte=sixty_days_ago,
            created_at__date__lt=thirty_days_ago
        )

        current_revenue = current_orders.filter(payment_status='paid').aggregate(
            total=Sum('total')
        )['total'] or 0
        previous_revenue = previous_orders.filter(payment_status='paid').aggregate(
            total=Sum('total')
        )['total'] or 0

        revenue_change = 0
        if previous_revenue > 0:
            revenue_change = round(((current_revenue - previous_revenue) / previous_revenue) * 100, 1)

        current_order_count = current_orders.count()
        previous_order_count = previous_orders.count()
        orders_change = 0
        if previous_order_count > 0:
            orders_change = round(((current_order_count - previous_order_count) / previous_order_count) * 100, 1)

        top_products = list(
            Order.objects.filter(
                created_at__date__gte=thirty_days_ago,
                payment_status='paid'
            ).values('items__product__name').annotate(
                total=Sum('items__total_price')
            ).order_by('-total')[:5]
        )

        recent_orders = list(
            Order.objects.order_by('-created_at')[:10].values(
                'order_number', 'total', 'status', 'created_at'
            )
        )

        revenue_chart = list(
            DailyStats.objects.filter(date__gte=thirty_days_ago)
            .order_by('date').values('date', 'total_revenue')
        )

        orders_chart = list(
            DailyStats.objects.filter(date__gte=thirty_days_ago)
            .order_by('date').values('date', 'total_orders')
        )

        return Response({
            'success': True,
            'dashboard': {
                'total_revenue': str(current_revenue),
                'total_orders': current_order_count,
                'total_customers': User.objects.filter(role='customer').count(),
                'total_products': Product.objects.filter(is_active=True).count(),
                'revenue_change': revenue_change,
                'orders_change': orders_change,
                'top_products': top_products,
                'recent_orders': recent_orders,
                'revenue_chart': revenue_chart,
                'orders_chart': orders_chart,
            }
        })
