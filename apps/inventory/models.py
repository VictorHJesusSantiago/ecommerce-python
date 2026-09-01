from django.db import models
from django.conf import settings
from decimal import Decimal
from apps.common.models import TimeStampedModel, UUIDModel, ActivatableModel


class Warehouse(UUIDModel, TimeStampedModel, ActivatableModel):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    address_line1 = models.CharField(max_length=255, blank=True, default='')
    address_line2 = models.CharField(max_length=255, blank=True, default='')
    city = models.CharField(max_length=100, blank=True, default='')
    state = models.CharField(max_length=100, blank=True, default='')
    postal_code = models.CharField(max_length=20, blank=True, default='')
    country = models.CharField(max_length=2, default='US')
    phone = models.CharField(max_length=20, blank=True, default='')
    email = models.EmailField(blank=True, default='')
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='managed_warehouses'
    )
    priority = models.PositiveIntegerField(default=0)
    shipping_cost_per_kg = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.50'))

    class Meta:
        verbose_name = 'Warehouse'
        verbose_name_plural = 'Warehouses'
        ordering = ['-priority', 'name']

    def __str__(self):
        return f"{self.name} ({self.code})"

    @property
    def total_items(self):
        return self.stock_items.aggregate(total=models.Sum('quantity'))['total'] or 0


class StockItem(UUIDModel, TimeStampedModel):
    product = models.ForeignKey(
        'products.Product', on_delete=models.CASCADE, related_name='stock_items'
    )
    variant = models.ForeignKey(
        'products.ProductVariant', on_delete=models.CASCADE,
        null=True, blank=True, related_name='stock_items'
    )
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='stock_items')
    quantity = models.IntegerField(default=0)
    reserved_quantity = models.IntegerField(default=0)
    low_stock_threshold = models.IntegerField(default=5)
    reorder_point = models.IntegerField(default=10)
    reorder_quantity = models.IntegerField(default=50)
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    location = models.CharField(max_length=100, blank=True, default='', help_text='Bin/shelf location')

    class Meta:
        verbose_name = 'Stock Item'
        verbose_name_plural = 'Stock Items'
        unique_together = ['product', 'variant', 'warehouse']

    def __str__(self):
        return f"{self.product.name} @ {self.warehouse.name}: {self.quantity}"

    @property
    def available_quantity(self):
        return max(0, self.quantity - self.reserved_quantity)

    @property
    def is_low_stock(self):
        return self.available_quantity <= self.low_stock_threshold

    @property
    def needs_reorder(self):
        return self.available_quantity <= self.reorder_point

    def adjust_stock(self, quantity_change, reason='', performed_by=None):
        old_qty = self.quantity
        self.quantity += quantity_change
        if self.quantity < 0:
            self.quantity = 0
        self.save(update_fields=['quantity', 'updated_at'])
        StockMovement.objects.create(
            stock_item=self,
            movement_type='adjustment' if quantity_change > 0 else 'sale',
            quantity=abs(quantity_change),
            reference=f'Stock adjustment: {reason}',
            performed_by=performed_by,
        )
        return old_qty, self.quantity

    def reserve_stock(self, quantity):
        if self.available_quantity >= quantity:
            self.reserved_quantity += quantity
            self.save(update_fields=['reserved_quantity', 'updated_at'])
            return True
        return False

    def release_reservation(self, quantity):
        self.reserved_quantity = max(0, self.reserved_quantity - quantity)
        self.save(update_fields=['reserved_quantity', 'updated_at'])

    def deduct_reserved(self, quantity):
        self.quantity -= quantity
        self.reserved_quantity = max(0, self.reserved_quantity - quantity)
        self.save(update_fields=['quantity', 'reserved_quantity', 'updated_at'])


class StockMovement(UUIDModel, TimeStampedModel):
    MOVEMENT_TYPES = [
        ('purchase', 'Purchase'),
        ('sale', 'Sale'),
        ('return', 'Return'),
        ('adjustment', 'Adjustment'),
        ('transfer', 'Transfer'),
        ('damaged', 'Damaged'),
        ('expired', 'Expired'),
        ('found', 'Found'),
    ]
    stock_item = models.ForeignKey(StockItem, on_delete=models.CASCADE, related_name='movements')
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.PositiveIntegerField()
    reference = models.CharField(max_length=200, blank=True, default='')
    notes = models.TextField(blank=True, default='')
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    related_order = models.ForeignKey(
        'orders.Order', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='stock_movements'
    )

    class Meta:
        verbose_name = 'Stock Movement'
        verbose_name_plural = 'Stock Movements'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.stock_item.product.name}"


class StockTransfer(UUIDModel, TimeStampedModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_transit', 'In Transit'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    source_warehouse = models.ForeignKey(
        Warehouse, on_delete=models.CASCADE, related_name='outgoing_transfers'
    )
    destination_warehouse = models.ForeignKey(
        Warehouse, on_delete=models.CASCADE, related_name='incoming_transfers'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, default='')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Stock Transfer'
        verbose_name_plural = 'Stock Transfers'
        ordering = ['-created_at']

    def __str__(self):
        return f"Transfer {self.id} from {self.source_warehouse} to {self.destination_warehouse}"


class StockTransferItem(UUIDModel):
    transfer = models.ForeignKey(StockTransfer, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    variant = models.ForeignKey(
        'products.ProductVariant', on_delete=models.SET_NULL, null=True, blank=True
    )
    quantity = models.PositiveIntegerField()

    class Meta:
        verbose_name = 'Stock Transfer Item'
        verbose_name_plural = 'Stock Transfer Items'

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"


class Supplier(UUIDModel, TimeStampedModel):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    contact_name = models.CharField(max_length=200, blank=True, default='')
    email = models.EmailField(blank=True, default='')
    phone = models.CharField(max_length=20, blank=True, default='')
    address = models.TextField(blank=True, default='')
    website = models.URLField(blank=True, default='')
    payment_terms = models.CharField(max_length=100, blank=True, default='')
    lead_time_days = models.PositiveIntegerField(default=7)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal('0.00'))
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, default='')

    class Meta:
        verbose_name = 'Supplier'
        verbose_name_plural = 'Suppliers'
        ordering = ['name']

    def __str__(self):
        return self.name


class PurchaseOrder(UUIDModel, TimeStampedModel):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('received', 'Received'),
        ('cancelled', 'Cancelled'),
    ]
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='purchase_orders')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    order_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    shipping_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    expected_delivery = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, default='')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    received_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Purchase Order'
        verbose_name_plural = 'Purchase Orders'
        ordering = ['-created_at']

    def __str__(self):
        return f"PO-{self.order_number}"

    def calculate_totals(self):
        self.subtotal = sum(item.line_total for item in self.items.all())
        self.total = self.subtotal + self.tax_amount + self.shipping_amount
        self.save(update_fields=['subtotal', 'total', 'updated_at'])


class PurchaseOrderItem(UUIDModel):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    variant = models.ForeignKey(
        'products.ProductVariant', on_delete=models.SET_NULL, null=True, blank=True
    )
    quantity = models.PositiveIntegerField()
    received_quantity = models.PositiveIntegerField(default=0)
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2)
    line_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    class Meta:
        verbose_name = 'Purchase Order Item'
        verbose_name_plural = 'Purchase Order Items'

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    def save(self, *args, **kwargs):
        self.line_total = self.unit_cost * self.quantity
        super().save(*args, **kwargs)


class InventoryLog(UUIDModel, TimeStampedModel):
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='inventory_logs')
    variant = models.ForeignKey(
        'products.ProductVariant', on_delete=models.SET_NULL, null=True, blank=True
    )
    warehouse = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=50)
    quantity_before = models.IntegerField(default=0)
    quantity_after = models.IntegerField(default=0)
    reference = models.CharField(max_length=200, blank=True, default='')
    notes = models.TextField(blank=True, default='')
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        verbose_name = 'Inventory Log'
        verbose_name_plural = 'Inventory Logs'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product.name} - {self.action}"
