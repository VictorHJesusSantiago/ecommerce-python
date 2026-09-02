from rest_framework import serializers
from .models import Transaction, Refund, PaymentGateway, PaymentMethod, WebhookEvent


class PaymentGatewaySerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentGateway
        fields = ['id', 'name', 'code', 'is_active', 'supported_currencies', 'fee_percent', 'fee_fixed']
        read_only_fields = ['id']


class TransactionSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id', 'gateway', 'order', 'transaction_id', 'reference_id', 'type',
            'status', 'status_display', 'type_display', 'amount', 'currency',
            'fee', 'net_amount', 'payment_method', 'card_last_four', 'card_brand',
            'error_message', 'metadata', 'processed_at', 'created_at',
        ]
        read_only_fields = [
            'id', 'transaction_id', 'fee', 'net_amount', 'gateway_response',
            'error_message', 'processed_at', 'created_at',
        ]


class TransactionListSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True, default=None)

    class Meta:
        model = Transaction
        fields = [
            'id', 'transaction_id', 'order_number', 'type', 'status',
            'status_display', 'amount', 'currency', 'payment_method',
            'card_last_four', 'card_brand', 'created_at',
        ]


class PaymentProcessSerializer(serializers.Serializer):
    order_id = serializers.UUIDField()
    payment_method_id = serializers.UUIDField(required=False, allow_null=True)
    token = serializers.CharField(required=False, allow_blank=True)
    save_payment_method = serializers.BooleanField(default=False)


class RefundSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    transaction_id = serializers.CharField(source='transaction.transaction_id', read_only=True)

    class Meta:
        model = Refund
        fields = [
            'id', 'transaction', 'transaction_id', 'order', 'refund_id',
            'amount', 'reason', 'status', 'status_display', 'processed_by',
            'processed_at', 'created_at',
        ]
        read_only_fields = [
            'id', 'refund_id', 'status', 'processed_by', 'processed_at', 'created_at'
        ]


class RefundCreateSerializer(serializers.Serializer):
    transaction_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0.01)
    reason = serializers.CharField()


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = [
            'id', 'gateway', 'payment_type', 'last_four', 'card_brand',
            'expiry_month', 'expiry_year', 'is_default', 'created_at',
        ]
        read_only_fields = ['id', 'last_four', 'card_brand', 'created_at']


class WebhookEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookEvent
        fields = ['id', 'event_id', 'event_type', 'payload', 'processed', 'processed_at', 'created_at']
        read_only_fields = fields


class PaymentStatsSerializer(serializers.Serializer):
    total_transactions = serializers.IntegerField()
    successful_transactions = serializers.IntegerField()
    failed_transactions = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_fees = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_refunds = serializers.DecimalField(max_digits=12, decimal_places=2)
    avg_transaction = serializers.DecimalField(max_digits=12, decimal_places=2)
