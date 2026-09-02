from django.contrib import admin
from .models import Transaction, Refund, PaymentGateway, PaymentMethod, WebhookEvent, PaymentLog


@admin.register(PaymentGateway)
class PaymentGatewayAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active', 'test_mode', 'fee_percent', 'fee_fixed']
    list_filter = ['is_active', 'test_mode']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'gateway', 'order', 'user', 'type', 'status', 'amount', 'currency', 'created_at']
    list_filter = ['gateway', 'type', 'status', 'currency']
    search_fields = ['transaction_id', 'order__order_number', 'user__email']
    readonly_fields = ['transaction_id', 'fee', 'net_amount', 'gateway_response', 'error_message', 'processed_at', 'created_at']


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ['refund_id', 'transaction', 'order', 'amount', 'status', 'processed_by', 'created_at']
    list_filter = ['status']
    search_fields = ['refund_id', 'order__order_number']
    readonly_fields = ['refund_id', 'processed_at', 'created_at']


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['user', 'payment_type', 'card_brand', 'last_four', 'is_default']
    list_filter = ['payment_type', 'card_brand', 'is_default']
    search_fields = ['user__email']


@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    list_display = ['event_id', 'event_type', 'gateway', 'processed', 'created_at']
    list_filter = ['gateway', 'processed', 'event_type']
    search_fields = ['event_id', 'event_type']
    readonly_fields = ['payload', 'processed_at', 'created_at']


@admin.register(PaymentLog)
class PaymentLogAdmin(admin.ModelAdmin):
    list_display = ['gateway_code', 'action', 'status_code', 'duration_ms', 'created_at']
    list_filter = ['gateway_code', 'action']
    readonly_fields = ['request_data', 'response_data', 'created_at']
