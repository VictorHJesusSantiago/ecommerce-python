from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class StockQuantityValidator:
    def __call__(self, value):
        if value < 0:
            raise ValidationError(_('Stock quantity cannot be negative.'))


class WarehouseCodeValidator:
    def __call__(self, value):
        if len(value) < 2 or len(value) > 20:
            raise ValidationError(_('Warehouse code must be 2-20 characters.'))
        if not value.isalnum():
            raise ValidationError(_('Warehouse code must be alphanumeric.'))


class TransferValidator:
    def validate_transfer(self, source, destination, items):
        if source == destination:
            raise ValidationError(_('Source and destination warehouses must be different.'))

        for item in items:
            stock = StockItem.objects.filter(
                product=item['product'], warehouse=source
            ).first()
            if not stock or stock.available_quantity < item['quantity']:
                raise ValidationError(
                    _('Insufficient stock for %(product)s in source warehouse.'),
                    params={'product': str(item['product'])}
                )
