from rest_framework import serializers
from .models import (
    Order, OrderItem, OrderStatusHistory, Shipment, ShipmentTracking,
    OrderNote, OrderPayment, ReturnRequest
)


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(read_only=True)
    product_sku = serializers.CharField(read_only=True)
    line_total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'variant', 'product_name', 'product_sku',
            'variant_name', 'quantity', 'unit_price', 'total_price',
            'tax_amount', 'discount_amount', 'is_refunded', 'refund_amount',
            'line_total', 'product_snapshot',
        ]


class OrderListSerializer(serializers.ModelSerializer):
    item_count = serializers.SerializerMethodField()
    shipping_full_name = serializers.CharField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'status_display', 'payment_status',
            'payment_status_display', 'total', 'currency', 'shipping_full_name',
            'item_count', 'created_at',
        ]

    def get_item_count(self, obj):
        return obj.items.count()


class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_history = serializers.SerializerMethodField()
    shipments = serializers.SerializerMethodField()
    payments = serializers.SerializerMethodField()
    shipping_full_name = serializers.CharField(read_only=True)
    shipping_full_address = serializers.CharField(read_only=True)
    can_cancel = serializers.BooleanField(read_only=True)
    can_refund = serializers.BooleanField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'payment_status', 'subtotal',
            'discount_amount', 'shipping_amount', 'tax_amount', 'total', 'currency',
            'shipping_first_name', 'shipping_last_name', 'shipping_company',
            'shipping_address_line1', 'shipping_address_line2', 'shipping_city',
            'shipping_state', 'shipping_postal_code', 'shipping_country',
            'shipping_phone', 'billing_same_as_shipping', 'billing_first_name',
            'billing_last_name', 'billing_company', 'billing_address_line1',
            'billing_address_line2', 'billing_city', 'billing_state',
            'billing_postal_code', 'billing_country', 'billing_phone',
            'coupon_code', 'customer_notes', 'admin_notes', 'tracking_number',
            'shipping_carrier', 'confirmed_at', 'shipped_at', 'delivered_at',
            'cancelled_at', 'paid_at', 'source', 'items', 'status_history',
            'shipments', 'payments', 'shipping_full_name', 'shipping_full_address',
            'can_cancel', 'can_refund', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'order_number', 'subtotal', 'total', 'confirmed_at',
            'shipped_at', 'delivered_at', 'cancelled_at', 'paid_at',
            'created_at', 'updated_at',
        ]

    def get_status_history(self, obj):
        history = obj.status_history.all()[:10]
        return OrderStatusHistorySerializer(history, many=True).data

    def get_shipments(self, obj):
        return ShipmentSerializer(obj.shipments.all(), many=True).data

    def get_payments(self, obj):
        return OrderPaymentSerializer(obj.payments.all(), many=True).data


class OrderCreateSerializer(serializers.Serializer):
    shipping_address_id = serializers.UUIDField(required=True)
    billing_address_id = serializers.UUIDField(required=False, allow_null=True)
    shipping_method = serializers.CharField(max_length=50, default='standard')
    payment_method = serializers.CharField(max_length=50)
    customer_notes = serializers.CharField(required=False, allow_blank=True, default='')
    coupon_code = serializers.CharField(required=False, allow_blank=True, default='')


class OrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)
    notes = serializers.CharField(required=False, allow_blank=True, default='')


class ShipmentCreateSerializer(serializers.Serializer):
    carrier = serializers.CharField(max_length=50)
    carrier_service = serializers.CharField(max_length=100, required=False, allow_blank=True, default='')
    tracking_number = serializers.CharField(max_length=100, required=False, allow_blank=True, default='')
    estimated_delivery = serializers.DateField(required=False, allow_null=True)
    weight = serializers.DecimalField(max_digits=8, decimal_places=2, required=False, allow_null=True)
    shipping_cost = serializers.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = serializers.CharField(required=False, allow_blank=True, default='')


class ShipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipment
        fields = [
            'id', 'tracking_number', 'carrier', 'carrier_service', 'status',
            'estimated_delivery', 'actual_delivery', 'weight', 'shipping_cost',
            'notes', 'shipped_at', 'delivered_at', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class ShipmentTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShipmentTracking
        fields = ['id', 'status', 'location', 'description', 'timestamp', 'data']
        read_only_fields = ['id']


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    changed_by_email = serializers.CharField(source='changed_by.email', read_only=True, default=None)

    class Meta:
        model = OrderStatusHistory
        fields = ['id', 'status', 'previous_status', 'notes', 'changed_by', 'changed_by_email', 'created_at']


class OrderNoteSerializer(serializers.ModelSerializer):
    created_by_email = serializers.CharField(source='created_by.email', read_only=True, default=None)

    class Meta:
        model = OrderNote
        fields = ['id', 'note', 'is_customer_visible', 'created_by', 'created_by_email', 'created_at']
        read_only_fields = ['id', 'created_by', 'created_at']


class OrderPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderPayment
        fields = [
            'id', 'payment_method', 'transaction_id', 'amount', 'currency',
            'status', 'gateway_response', 'paid_at', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class ReturnRequestSerializer(serializers.ModelSerializer):
    order_item_detail = OrderItemSerializer(source='order_item', read_only=True)

    class Meta:
        model = ReturnRequest
        fields = [
            'id', 'order', 'order_item', 'order_item_detail', 'reason',
            'quantity', 'status', 'refund_amount', 'admin_notes',
            'processed_by', 'processed_at', 'created_at',
        ]
        read_only_fields = ['id', 'status', 'refund_amount', 'processed_by', 'processed_at', 'created_at']


class ReturnRequestCreateSerializer(serializers.Serializer):
    order_item_id = serializers.UUIDField()
    reason = serializers.CharField()
    quantity = serializers.IntegerField(min_value=1)


class OrderStatsSerializer(serializers.Serializer):
    total_orders = serializers.IntegerField()
    pending_orders = serializers.IntegerField()
    processing_orders = serializers.IntegerField()
    shipped_orders = serializers.IntegerField()
    delivered_orders = serializers.IntegerField()
    cancelled_orders = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    average_order_value = serializers.DecimalField(max_digits=12, decimal_places=2)
