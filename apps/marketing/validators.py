from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re


class CouponCodeValidator:
    def __call__(self, value):
        if not re.match(r'^[A-Z0-9]+$', value.upper()):
            raise ValidationError(_('Coupon code must contain only uppercase letters and numbers.'))
        if len(value) < 3 or len(value) > 50:
            raise ValidationError(_('Coupon code must be 3-50 characters long.'))


class DiscountValueValidator:
    def __init__(self, discount_type='percentage'):
        self.discount_type = discount_type

    def __call__(self, value):
        if value <= 0:
            raise ValidationError(_('Discount value must be positive.'))
        if self.discount_type == 'percentage' and value > 100:
            raise ValidationError(_('Percentage discount cannot exceed 100%.'))
