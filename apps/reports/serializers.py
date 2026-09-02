from rest_framework import serializers
from .models import Report, AnalyticsEvent, DailyStats, ProductPerformance, SalesForecast


class ReportSerializer(serializers.ModelSerializer):
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Report
        fields = [
            'id', 'name', 'report_type', 'report_type_display', 'status',
            'status_display', 'date_from', 'date_to', 'filters', 'data',
            'file', 'generated_by', 'completed_at', 'error_message',
            'created_at',
        ]
        read_only_fields = [
            'id', 'status', 'data', 'file', 'generated_by',
            'completed_at', 'error_message', 'created_at',
        ]


class ReportCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    report_type = serializers.ChoiceField(choices=Report.REPORT_TYPES)
    date_from = serializers.DateField(required=False, allow_null=True)
    date_to = serializers.DateField(required=False, allow_null=True)
    filters = serializers.JSONField(required=False, default=dict)


class AnalyticsEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalyticsEvent
        fields = [
            'id', 'event_type', 'page_url', 'product', 'data',
            'revenue', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class DailyStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyStats
        fields = [
            'id', 'date', 'total_orders', 'total_revenue', 'total_items_sold',
            'average_order_value', 'new_customers', 'returning_customers',
            'page_views', 'unique_visitors', 'conversion_rate',
            'refund_count', 'refund_amount',
        ]


class ProductPerformanceSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = ProductPerformance
        fields = [
            'id', 'product', 'product_name', 'date', 'views',
            'add_to_carts', 'purchases', 'revenue', 'conversion_rate',
        ]


class SalesForecastSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesForecast
        fields = [
            'id', 'date', 'predicted_revenue', 'predicted_orders',
            'confidence', 'actual_revenue', 'actual_orders',
        ]


class DashboardSerializer(serializers.Serializer):
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_orders = serializers.IntegerField()
    total_customers = serializers.IntegerField()
    total_products = serializers.IntegerField()
    revenue_change = serializers.FloatField()
    orders_change = serializers.FloatField()
    top_products = serializers.ListField()
    recent_orders = serializers.ListField()
    revenue_chart = serializers.ListField()
    orders_chart = serializers.ListField()
