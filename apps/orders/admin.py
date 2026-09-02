from django.contrib import admin
from .models import (
    Order, OrderItem, OrderStatusHistory, Shipment, ShipmentTracking,
    OrderNote, OrderPayment, ReturnRequest
)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'product_sku', 'unit_price', 'total_price']
    fields = ['product_name', 'product_sku', 'variant_name', 'quantity', 'unit_price', 'total_price', 'is_refunded']


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ['status', 'previous_status', 'notes', 'changed_by', 'created_at']
    ordering = ['-created_at']


class OrderNoteInline(admin.TabularInline):
    model = OrderNote
    extra = 0
    fields = ['note', 'is_customer_visible', 'created_by', 'created_at']
    readonly_fields = ['created_at']


class OrderPaymentInline(admin.TabularInline):
    model = OrderPayment
    extra = 0
    readonly_fields = ['payment_method', 'transaction_id', 'amount', 'status', 'paid_at', 'created_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 'user', 'status', 'payment_status', 'total',
        'shipping_full_name', 'created_at'
    ]
    list_filter = ['status', 'payment_status', 'currency', 'source']
    search_fields = ['order_number', 'user__email', 'shipping_first_name', 'shipping_last_name']
    readonly_fields = [
        'order_number', 'subtotal', 'total', 'confirmed_at', 'shipped_at',
        'delivered_at', 'cancelled_at', 'paid_at', 'created_at', 'updated_at'
    ]
    inlines = [OrderItemInline, OrderStatusHistoryInline, OrderNoteInline, OrderPaymentInline]
    fieldsets = (
        ('Order Info', {
            'fields': ('order_number', 'user', 'status', 'payment_status', 'source', 'ip_address')
        }),
        ('Shipping Address', {
            'fields': ('shipping_first_name', 'shipping_last_name', 'shipping_company',
                       'shipping_address_line1', 'shipping_address_line2', 'shipping_city',
                       'shipping_state', 'shipping_postal_code', 'shipping_country', 'shipping_phone')
        }),
        ('Billing', {
            'fields': ('billing_same_as_shipping', 'billing_first_name', 'billing_last_name',
                       'billing_company', 'billing_address_line1', 'billing_address_line2',
                       'billing_city', 'billing_state', 'billing_postal_code', 'billing_country', 'billing_phone')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'discount_amount', 'shipping_amount', 'tax_amount', 'total', 'currency')
        }),
        ('Coupon', {
            'fields': ('coupon', 'coupon_code')
        }),
        ('Shipping', {
            'fields': ('tracking_number', 'shipping_carrier')
        }),
        ('Notes', {
            'fields': ('customer_notes', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('confirmed_at', 'shipped_at', 'delivered_at', 'cancelled_at', 'paid_at', 'created_at', 'updated_at')
        }),
    )
    actions = ['confirm_orders', 'mark_as_shipped', 'mark_as_delivered']

    def confirm_orders(self, request, queryset):
        for order in queryset.filter(status='pending'):
            order.confirm()
    confirm_orders.short_description = "Confirm selected orders"

    def mark_as_shipped(self, request, queryset):
        for order in queryset.filter(status='confirmed'):
            order.ship()
    mark_as_shipped.short_description = "Mark selected orders as shipped"

    def mark_as_delivered(self, request, queryset):
        for order in queryset.filter(status='shipped'):
            order.deliver()
    mark_as_delivered.short_description = "Mark selected orders as delivered"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product_name', 'product_sku', 'quantity', 'unit_price', 'total_price', 'is_refunded']
    search_fields = ['order__order_number', 'product_name', 'product_sku']


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ['tracking_number', 'order', 'carrier', 'status', 'estimated_delivery', 'shipped_at']
    list_filter = ['carrier', 'status']
    search_fields = ['tracking_number', 'order__order_number']
    readonly_fields = ['shipped_at', 'delivered_at', 'created_at']


@admin.register(ShipmentTracking)
class ShipmentTrackingAdmin(admin.ModelAdmin):
    list_display = ['shipment', 'status', 'location', 'timestamp']
    list_filter = ['status']
    readonly_fields = ['timestamp']


@admin.register(OrderNote)
class OrderNoteAdmin(admin.ModelAdmin):
    list_display = ['order', 'note', 'is_customer_visible', 'created_by', 'created_at']
    list_filter = ['is_customer_visible']
    readonly_fields = ['created_at']


@admin.register(OrderPayment)
class OrderPaymentAdmin(admin.ModelAdmin):
    list_display = ['order', 'payment_method', 'amount', 'status', 'paid_at']
    list_filter = ['payment_method', 'status']
    readonly_fields = ['paid_at', 'created_at']


@admin.register(ReturnRequest)
class ReturnRequestAdmin(admin.ModelAdmin):
    list_display = ['order', 'order_item', 'reason', 'quantity', 'status', 'refund_amount', 'created_at']
    list_filter = ['status']
    search_fields = ['order__order_number']
    readonly_fields = ['refund_amount', 'processed_at', 'created_at']
