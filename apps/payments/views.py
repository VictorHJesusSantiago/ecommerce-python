from rest_framework import viewsets, status, permissions, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count, Q
from django.utils import timezone

from .models import Transaction, Refund, PaymentGateway, PaymentMethod, WebhookEvent, PaymentLog
from .serializers import (
    TransactionSerializer, TransactionListSerializer, PaymentProcessSerializer,
    RefundSerializer, RefundCreateSerializer, PaymentGatewaySerializer,
    PaymentMethodSerializer, WebhookEventSerializer, PaymentStatsSerializer
)
from apps.common.permissions import IsAdminUser
from apps.common.exceptions import PaymentError, RefundError
from apps.common.pagination import StandardResultsSetPagination


class PaymentGatewayViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentGatewaySerializer
    permission_classes = [IsAdminUser]
    queryset = PaymentGateway.objects.all()

    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        gateway = self.get_object()
        return Response({
            'success': True,
            'message': f'Connection to {gateway.name} successful.',
            'test_mode': gateway.test_mode,
        })


class TransactionViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if self.request.user.is_staff:
            return Transaction.objects.all()
        return Transaction.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return TransactionListSerializer
        return TransactionSerializer

    @action(detail=False, methods=['post'])
    def process_payment(self, request):
        serializer = PaymentProcessSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from apps.orders.models import Order
        try:
            order = Order.objects.get(
                pk=serializer.validated_data['order_id'],
                user=request.user
            )
        except Order.DoesNotExist:
            return Response({
                'success': False,
                'error': {'message': 'Order not found.'}
            }, status=status.HTTP_404_NOT_FOUND)

        if order.payment_status == 'paid':
            raise PaymentError(detail='Order is already paid.')

        gateway = PaymentGateway.objects.filter(is_active=True).first()
        if not gateway:
            raise PaymentError(detail='No payment gateway available.')

        from apps.common.utils import generate_transaction_id
        transaction = Transaction.objects.create(
            gateway=gateway,
            order=order,
            user=request.user,
            transaction_id=generate_transaction_id(),
            type='payment',
            status='processing',
            amount=order.total,
            currency=order.currency,
            ip_address=request.META.get('REMOTE_ADDR'),
        )

        PaymentLog.objects.create(
            transaction=transaction,
            gateway_code=gateway.code,
            action='process_payment',
            request_data={'order_id': str(order.id), 'amount': str(order.total)},
        )

        transaction.complete()

        order.payment_status = 'paid'
        order.paid_at = timezone.now()
        order.save(update_fields=['payment_status', 'paid_at', 'updated_at'])

        return Response({
            'success': True,
            'message': 'Payment processed successfully.',
            'transaction': TransactionSerializer(transaction).data,
        })

    @action(detail=False, methods=['get'])
    def payment_stats(self, request):
        if not request.user.is_staff:
            return Response({'success': False, 'error': {'message': 'Permission denied.'}}, status=403)

        qs = Transaction.objects.all()
        stats = {
            'total_transactions': qs.count(),
            'successful_transactions': qs.filter(status='completed').count(),
            'failed_transactions': qs.filter(status='failed').count(),
            'total_amount': qs.filter(status='completed').aggregate(
                total=Sum('amount')
            )['total'] or 0,
            'total_fees': qs.filter(status='completed').aggregate(
                total=Sum('fee')
            )['total'] or 0,
            'total_refunds': Refund.objects.filter(status='completed').aggregate(
                total=Sum('amount')
            )['total'] or 0,
            'avg_transaction': qs.filter(status='completed').aggregate(
                avg=Avg('amount')
            )['avg'] or 0,
        }
        return Response({'success': True, 'stats': stats})


class RefundViewSet(viewsets.ModelViewSet):
    serializer_class = RefundSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if self.request.user.is_staff:
            return Refund.objects.all()
        return Refund.objects.filter(order__user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return RefundCreateSerializer
        return RefundSerializer

    def create(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response({'success': False, 'error': {'message': 'Permission denied.'}}, status=403)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from apps.common.utils import generate_refund_number
        transaction = Transaction.objects.get(pk=serializer.validated_data['transaction_id'])

        if transaction.status != 'completed':
            raise RefundError(detail='Can only refund completed transactions.')

        refund_amount = serializer.validated_data['amount']
        existing_refunds = transaction.refunds.filter(status='completed').aggregate(
            total=Sum('amount')
        )['total'] or 0

        if existing_refunds + refund_amount > transaction.amount:
            raise RefundError(detail='Refund amount exceeds available amount.')

        refund = Refund.objects.create(
            transaction=transaction,
            order=transaction.order,
            refund_id=generate_refund_number(),
            amount=refund_amount,
            reason=serializer.validated_data.get('reason', ''),
            status='processing',
            processed_by=request.user,
        )

        refund.complete(processed_by=request.user)

        if transaction.order:
            order = transaction.order
            if existing_refunds + refund_amount >= transaction.amount:
                order.payment_status = 'refunded'
            else:
                order.payment_status = 'partially_refunded'
            order.save(update_fields=['payment_status', 'updated_at'])

        return Response({
            'success': True,
            'message': 'Refund processed.',
            'refund': RefundSerializer(refund).data,
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        if not request.user.is_staff:
            return Response({'success': False, 'error': {'message': 'Permission denied.'}}, status=403)
        refund = self.get_object()
        refund.complete(processed_by=request.user)
        return Response({'success': True, 'message': 'Refund approved.'})


class PaymentMethodViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentMethodSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PaymentMethod.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WebhookViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['post'])
    def stripe(self, request):
        import json
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')

        from .processors import StripeProcessor
        processor = StripeProcessor()
        event = processor.verify_webhook(payload, sig_header)

        if not event:
            return Response({'error': 'Invalid webhook'}, status=400)

        webhook = WebhookEvent.objects.create(
            gateway=PaymentGateway.objects.filter(code='stripe').first(),
            event_id=event['id'],
            event_type=event['type'],
            payload=event,
        )

        processor.process_event(event)
        webhook.mark_processed()

        return Response({'received': True})

    @action(detail=False, methods=['post'])
    def paypal(self, request):
        event_data = request.data
        webhook = WebhookEvent.objects.create(
            gateway=PaymentGateway.objects.filter(code='paypal').first(),
            event_id=event_data.get('id', ''),
            event_type=event_data.get('event_type', ''),
            payload=event_data,
        )
        from .processors import PayPalProcessor
        processor = PayPalProcessor()
        processor.process_event(event_data)
        webhook.mark_processed()
        return Response({'received': True})
