from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class CartQuantityValidator:
    def __init__(self, min_qty=1, max_qty=99):
        self.min_qty = min_qty
        self.max_qty = max_qty

    def __call__(self, value):
        if value < self.min_qty:
            raise ValidationError(
                _('Quantity must be at least %(min)d.'),
                params={'min': self.min_qty}
            )
        if value > self.max_qty:
            raise ValidationError(
                _('Quantity cannot exceed %(max)d.'),
                params={'max': self.max_qty}
            )


class CartItemValidator:
    def __call__(self, cart, product, variant=None, quantity=1):
        from apps.common.exceptions import InsufficientStockError
        if product.track_inventory:
            stock = variant.quantity if variant else product.quantity
            existing = cart.items.filter(product=product, variant=variant).first()
            existing_qty = existing.quantity if existing else 0
            if stock < (existing_qty + quantity) and not product.allow_backorder:
                raise InsufficientStockError(
                    detail=f'Only {max(0, stock - existing_qty)} more items available in stock.'
                )


class CartLimitValidator:
    MAX_ITEMS = 50
    MAX_QUANTITY_PER_ITEM = 99

    def validate_total_items(self, cart, new_item=True):
        current = cart.items.count()
        if new_item:
            current += 1
        if current > self.MAX_ITEMS:
            raise ValidationError(
                _('Cart cannot contain more than %(max)d different items.'),
                params={'max': self.MAX_ITEMS}
            )

    def validate_quantity(self, quantity):
        if quantity > self.MAX_QUANTITY_PER_ITEM:
            raise ValidationError(
                _('Cannot add more than %(max)d of the same item.'),
                params={'max': self.MAX_QUANTITY_PER_ITEM}
            )
