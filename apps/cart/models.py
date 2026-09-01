from django.db import models
from django.conf import settings
from decimal import Decimal
from apps.common.models import TimeStampedModel, UUIDModel, ActivatableModel


class Cart(UUIDModel, TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        null=True, blank=True, related_name='carts'
    )
    session_key = models.CharField(max_length=255, blank=True, default='', db_index=True)
    is_active = models.BooleanField(default=True)
    coupon = models.ForeignKey(
        'marketing.Coupon', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='carts'
    )
    notes = models.TextField(blank=True, default='')
    currency = models.CharField(max_length=3, default='USD')

    class Meta:
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'
        ordering = ['-created_at']

    def __str__(self):
        if self.user:
            return f"Cart for {self.user.email}"
        return f"Cart {self.session_key}"

    @property
    def subtotal(self):
        return sum(item.line_total for item in self.items.all())

    @property
    def discount_amount(self):
        if self.coupon:
            return self.coupon.calculate_discount(self.subtotal)
        return Decimal('0.00')

    @property
    def total(self):
        return self.subtotal - self.discount_amount

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def total_items_count(self):
        return self.items.count()

    def clear(self):
        self.items.all().delete()
        self.coupon = None
        self.save(update_fields=['coupon', 'updated_at'])

    def add_item(self, product, quantity=1, variant=None):
        item, created = CartItem.objects.get_or_create(
            cart=self, product=product, variant=variant,
            defaults={'quantity': quantity}
        )
        if not created:
            item.quantity += quantity
            item.save(update_fields=['quantity', 'updated_at'])
        return item

    def remove_item(self, item_id):
        try:
            item = self.items.get(pk=item_id)
            item.delete()
            return True
        except CartItem.DoesNotExist:
            return False

    def update_item_quantity(self, item_id, quantity):
        try:
            item = self.items.get(pk=item_id)
            if quantity <= 0:
                item.delete()
                return None
            item.quantity = quantity
            item.save(update_fields=['quantity', 'updated_at'])
            return item
        except CartItem.DoesNotExist:
            return None


class CartItem(UUIDModel, TimeStampedModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(
        'products.Product', on_delete=models.CASCADE, related_name='cart_items'
    )
    variant = models.ForeignKey(
        'products.ProductVariant', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='cart_items'
    )
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True, default='')

    class Meta:
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        unique_together = ['cart', 'product', 'variant']
        ordering = ['created_at']

    def __str__(self):
        return f"{self.quantity}x {self.product.name} in Cart"

    def save(self, *args, **kwargs):
        if self.price is None:
            if self.variant:
                self.price = self.variant.price
            else:
                self.price = self.product.price
        super().save(*args, **kwargs)

    @property
    def unit_price(self):
        if self.variant:
            return self.variant.price
        return self.product.price

    @property
    def line_total(self):
        return self.unit_price * self.quantity

    @property
    def is_available(self):
        if self.variant:
            return self.variant.is_in_stock and self.variant.quantity >= self.quantity
        if not self.product.track_inventory:
            return True
        return self.product.quantity >= self.quantity or self.product.allow_backorder


class SavedItem(UUIDModel, TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='saved_items'
    )
    product = models.ForeignKey(
        'products.Product', on_delete=models.CASCADE,
        related_name='saved_items'
    )
    notes = models.TextField(blank=True, default='')

    class Meta:
        verbose_name = 'Saved Item'
        verbose_name_plural = 'Saved Items'
        unique_together = ['user', 'product']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product.name} saved by {self.user.email}"


class CartHistory(UUIDModel, TimeStampedModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='history')
    action = models.CharField(max_length=50)
    details = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = 'Cart History'
        verbose_name_plural = 'Cart Histories'
        ordering = ['-created_at']

    def __str__(self):
        return f"Cart {self.cart.pk} - {self.action}"

    @classmethod
    def log(cls, cart, action, details=None):
        return cls.objects.create(cart=cart, action=action, details=details or {})
