from django.db import models
from django.conf import settings
from decimal import Decimal
from django.core.validators import MinValueValidator
from apps.common.models import TimeStampedModel, UUIDModel, SoftDeleteModel
from apps.common.utils import generate_order_number, generate_tracking_number


class Order(UUIDModel, TimeStampedModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
        ('partially_refunded', 'Partially Refunded'),
        ('on_hold', 'On Hold'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('partially_paid', 'Partially Paid'),
        ('refunded', 'Refunded'),
        ('partially_refunded', 'Partially Refunded'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='orders'
    )
    order_number = models.CharField(max_length=50, unique=True, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')

    # Pricing
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    shipping_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    currency = models.CharField(max_length=3, default='USD')

    # Addresses
    shipping_first_name = models.CharField(max_length=100)
    shipping_last_name = models.CharField(max_length=100)
    shipping_company = models.CharField(max_length=150, blank=True, default='')
    shipping_address_line1 = models.CharField(max_length=255)
    shipping_address_line2 = models.CharField(max_length=255, blank=True, default='')
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100)
    shipping_postal_code = models.CharField(max_length=20)
    shipping_country = models.CharField(max_length=2, default='US')
    shipping_phone = models.CharField(max_length=20, blank=True, default='')

    billing_same_as_shipping = models.BooleanField(default=True)
    billing_first_name = models.CharField(max_length=100, blank=True, default='')
    billing_last_name = models.CharField(max_length=100, blank=True, default='')
    billing_company = models.CharField(max_length=150, blank=True, default='')
    billing_address_line1 = models.CharField(max_length=255, blank=True, default='')
    billing_address_line2 = models.CharField(max_length=255, blank=True, default='')
    billing_city = models.CharField(max_length=100, blank=True, default='')
    billing_state = models.CharField(max_length=100, blank=True, default='')
    billing_postal_code = models.CharField(max_length=20, blank=True, default='')
    billing_country = models.CharField(max_length=2, default='US')
    billing_phone = models.CharField(max_length=20, blank=True, default='')

    # Coupon
    coupon = models.ForeignKey(
        'marketing.Coupon', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='orders'
    )
    coupon_code = models.CharField(max_length=50, blank=True, default='')

    # Notes
    customer_notes = models.TextField(blank=True, default='')
    admin_notes = models.TextField(blank=True, default='')

    # Tracking
    tracking_number = models.CharField(max_length=100, blank=True, default='')
    shipping_carrier = models.CharField(max_length=50, blank=True, default='')

    # Timestamps
    confirmed_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    # Source
    source = models.CharField(max_length=50, default='web')
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['payment_status']),
        ]

    def __str__(self):
        return f"Order {self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = generate_order_number()
        super().save(*args, **kwargs)

    @property
    def shipping_full_name(self):
        return f"{self.shipping_first_name} {self.shipping_last_name}"

    @property
    def shipping_full_address(self):
        lines = [self.shipping_address_line1]
        if self.shipping_address_line2:
            lines.append(self.shipping_address_line2)
        lines.append(f"{self.shipping_city}, {self.shipping_state} {self.shipping_postal_code}")
        lines.append(self.shipping_country)
        return '\n'.join(lines)

    @property
    def can_cancel(self):
        return self.status in ('pending', 'confirmed')

    @property
    def can_refund(self):
        return self.payment_status == 'paid' and self.status in ('delivered', 'cancelled')

    def calculate_totals(self):
        from .models import OrderItem
        self.subtotal = sum(item.line_total for item in self.items.all())
        self.total = self.subtotal + self.shipping_amount + self.tax_amount - self.discount_amount
        self.save(update_fields=['subtotal', 'total', 'updated_at'])

    def confirm(self):
        from django.utils import timezone
        self.status = 'confirmed'
        self.confirmed_at = timezone.now()
        self.save(update_fields=['status', 'confirmed_at', 'updated_at'])

    def ship(self, tracking_number=None, carrier=None):
        from django.utils import timezone
        self.status = 'shipped'
        self.shipped_at = timezone.now()
        if tracking_number:
            self.tracking_number = tracking_number
        if carrier:
            self.shipping_carrier = carrier
        if not self.tracking_number:
            self.tracking_number = generate_tracking_number()
        self.save(update_fields=['status', 'shipped_at', 'tracking_number', 'shipping_carrier', 'updated_at'])

    def deliver(self):
        from django.utils import timezone
        self.status = 'delivered'
        self.delivered_at = timezone.now()
        self.save(update_fields=['status', 'delivered_at', 'updated_at'])

    def cancel(self, reason=''):
        from django.utils import timezone
        self.status = 'cancelled'
        self.cancelled_at = timezone.now()
        if reason:
            self.admin_notes = f"{self.admin_notes}\nCancellation reason: {reason}"
        self.save(update_fields=['status', 'cancelled_at', 'admin_notes', 'updated_at'])
        for item in self.items.all():
            if item.product.track_inventory:
                item.product.quantity += item.quantity
                item.product.save(update_fields=['quantity'])


class OrderItem(UUIDModel, TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(
        'products.Product', on_delete=models.SET_NULL, null=True,
        related_name='order_items'
    )
    variant = models.ForeignKey(
        'products.ProductVariant', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='order_items'
    )
    product_name = models.CharField(max_length=500)
    product_sku = models.CharField(max_length=50)
    variant_name = models.CharField(max_length=255, blank=True, default='')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    total_price = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    is_refunded = models.BooleanField(default=False)
    refund_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    product_snapshot = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.quantity}x {self.product_name} in Order {self.order.order_number}"

    def save(self, *args, **kwargs):
        if not self.total_price:
            self.total_price = self.unit_price * self.quantity
        if not self.product_snapshot and self.product:
            self.product_snapshot = {
                'name': self.product.name,
                'sku': self.product.sku,
                'price': str(self.unit_price),
                'image': self.product.images.first().image.url if self.product.images.exists() else '',
            }
        super().save(*args, **kwargs)

    @property
    def line_total(self):
        return self.unit_price * self.quantity


class OrderStatusHistory(UUIDModel, TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=20)
    previous_status = models.CharField(max_length=20, blank=True, default='')
    notes = models.TextField(blank=True, default='')
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True
    )

    class Meta:
        verbose_name = 'Order Status History'
        verbose_name_plural = 'Order Status Histories'
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.order.order_number} - {self.status}"

    @classmethod
    def log_status_change(cls, order, new_status, notes='', changed_by=None):
        previous = order.status
        cls.objects.create(
            order=order,
            status=new_status,
            previous_status=previous,
            notes=notes,
            changed_by=changed_by,
        )


class Shipment(UUIDModel, TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='shipments')
    tracking_number = models.CharField(max_length=100, unique=True)
    carrier = models.CharField(max_length=50)
    carrier_service = models.CharField(max_length=100, blank=True, default='')
    status = models.CharField(
        max_length=20,
        choices=[
            ('preparing', 'Preparing'),
            ('shipped', 'Shipped'),
            ('in_transit', 'In Transit'),
            ('out_for_delivery', 'Out for Delivery'),
            ('delivered', 'Delivered'),
            ('failed', 'Failed Delivery'),
            ('returned', 'Returned'),
        ],
        default='preparing'
    )
    estimated_delivery = models.DateField(null=True, blank=True)
    actual_delivery = models.DateField(null=True, blank=True)
    weight = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    notes = models.TextField(blank=True, default='')
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Shipment'
        verbose_name_plural = 'Shipments'
        ordering = ['-created_at']

    def __str__(self):
        return f"Shipment {self.tracking_number} for Order {self.order.order_number}"

    def mark_shipped(self):
        from django.utils import timezone
        self.status = 'shipped'
        self.shipped_at = timezone.now()
        self.save(update_fields=['status', 'shipped_at', 'updated_at'])

    def mark_delivered(self):
        from django.utils import timezone
        self.status = 'delivered'
        self.delivered_at = timezone.now()
        self.save(update_fields=['status', 'delivered_at', 'updated_at'])


class ShipmentTracking(UUIDModel):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='tracking_events')
    status = models.CharField(max_length=100)
    location = models.CharField(max_length=255, blank=True, default='')
    description = models.TextField(blank=True, default='')
    timestamp = models.DateTimeField()
    data = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = 'Shipment Tracking'
        verbose_name_plural = 'Shipment Tracking Events'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.shipment.tracking_number} - {self.status}"


class OrderNote(UUIDModel, TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='notes')
    note = models.TextField()
    is_customer_visible = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True
    )

    class Meta:
        verbose_name = 'Order Note'
        verbose_name_plural = 'Order Notes'
        ordering = ['-created_at']

    def __str__(self):
        return f"Note on Order {self.order.order_number}"


class OrderPayment(UUIDModel, TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    payment_method = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=200, blank=True, default='')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
            ('refunded', 'Refunded'),
            ('partially_refunded', 'Partially Refunded'),
        ],
        default='pending'
    )
    gateway_response = models.JSONField(default=dict, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Order Payment'
        verbose_name_plural = 'Order Payments'
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment ${self.amount} for Order {self.order.order_number}"

    def mark_completed(self):
        from django.utils import timezone
        self.status = 'completed'
        self.paid_at = timezone.now()
        self.save(update_fields=['status', 'paid_at', 'updated_at'])
        self.order.payment_status = 'paid'
        self.order.paid_at = timezone.now()
        self.order.save(update_fields=['payment_status', 'paid_at', 'updated_at'])


class ReturnRequest(UUIDModel, TimeStampedModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='returns')
    order_item = models.ForeignKey(
        OrderItem, on_delete=models.CASCADE, related_name='return_requests'
    )
    reason = models.TextField()
    quantity = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    refund_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    admin_notes = models.TextField(blank=True, default='')
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Return Request'
        verbose_name_plural = 'Return Requests'
        ordering = ['-created_at']

    def __str__(self):
        return f"Return for Order {self.order.order_number}"

    def approve(self, processed_by=None):
        from django.utils import timezone
        self.status = 'approved'
        self.processed_by = processed_by
        self.processed_at = timezone.now()
        self.save(update_fields=['status', 'processed_by', 'processed_at', 'updated_at'])

    def reject(self, notes='', processed_by=None):
        from django.utils import timezone
        self.status = 'rejected'
        self.admin_notes = notes
        self.processed_by = processed_by
        self.processed_at = timezone.now()
        self.save(update_fields=['status', 'admin_notes', 'processed_by', 'processed_at', 'updated_at'])

    def complete(self, processed_by=None):
        from django.utils import timezone
        self.status = 'completed'
        self.processed_by = processed_by
        self.processed_at = timezone.now()
        self.save(update_fields=['status', 'processed_by', 'processed_at', 'updated_at'])
        if self.order_item.product and self.order_item.product.track_inventory:
            self.order_item.product.quantity += self.quantity
            self.order_item.product.save(update_fields=['quantity'])
