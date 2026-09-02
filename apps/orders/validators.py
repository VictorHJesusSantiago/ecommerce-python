from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class OrderStatusValidator:
    VALID_TRANSITIONS = {
        'pending': ['confirmed', 'cancelled', 'on_hold'],
        'confirmed': ['processing', 'cancelled', 'on_hold'],
        'processing': ['shipped', 'cancelled', 'on_hold'],
        'shipped': ['delivered'],
        'delivered': ['refunded', 'partially_refunded'],
        'cancelled': [],
        'refunded': [],
        'partially_refunded': [],
        'on_hold': ['pending', 'confirmed', 'processing', 'cancelled'],
    }

    def __call__(self, order, new_status):
        current = order.status
        valid = self.VALID_TRANSITIONS.get(current, [])
        if new_status not in valid:
            raise ValidationError(
                _('Cannot transition from %(current)s to %(new)s.'),
                params={'current': current, 'new': new_status}
            )


class ShippingAddressValidator:
    def __call__(self, address_data):
        required_fields = ['first_name', 'last_name', 'address_line1', 'city', 'state', 'postal_code', 'country']
        for field in required_fields:
            if not address_data.get(field):
                raise ValidationError(
                    _('%(field)s is required for shipping address.'),
                    params={'field': field}
                )
        postal_code = address_data.get('postal_code', '')
        if len(postal_code) < 3:
            raise ValidationError(_('Invalid postal code.'))


class OrderQuantityValidator:
    def __call__(self, items):
        for item in items:
            if item['quantity'] < 1:
                raise ValidationError(_('Quantity must be at least 1.'))
            if item['quantity'] > 100:
                raise ValidationError(_('Maximum quantity per item is 100.'))


class ReturnRequestValidator:
    def __call__(self, order_item, quantity, reason):
        if not reason:
            raise ValidationError(_('Reason is required for return requests.'))
        if quantity > order_item.quantity:
            raise ValidationError(_('Return quantity cannot exceed ordered quantity.'))
        if quantity < 1:
            raise ValidationError(_('Return quantity must be at least 1.'))
