from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
import re


class ProductSKUValidator:
    def __call__(self, value):
        if not re.match(r'^[A-Z0-9\-]{2,50}$', value):
            raise ValidationError(_('SKU must be 2-50 uppercase alphanumeric characters or hyphens.'))


class PriceRangeValidator:
    def __init__(self, min_price=Decimal('0.01'), max_price=Decimal('999999.99')):
        self.min_price = min_price
        self.max_price = max_price

    def __call__(self, value):
        if value < self.min_price:
            raise ValidationError(
                _('Price must be at least %(min)s.'),
                params={'min': self.min_price}
            )
        if value > self.max_price:
            raise ValidationError(
                _('Price cannot exceed %(max)s.'),
                params={'max': self.max_price}
            )


class ProductWeightValidator:
    def __call__(self, value):
        if value is not None and value <= 0:
            raise ValidationError(_('Weight must be a positive number.'))
        if value is not None and value > 9999:
            raise ValidationError(_('Weight cannot exceed 9999 kg.'))


class ProductDimensionValidator:
    def __init__(self, max_value=9999):
        self.max_value = max_value

    def __call__(self, value):
        if value is not None and value <= 0:
            raise ValidationError(_('Dimension must be a positive number.'))
        if value is not None and value > self.max_value:
            raise ValidationError(
                _('Dimension cannot exceed %(max)s.'),
                params={'max': self.max_value}
            )


class ProductImageValidator:
    ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
    MAX_SIZE_MB = 10

    def __call__(self, value):
        if hasattr(value, 'content_type'):
            if value.content_type not in self.ALLOWED_TYPES:
                raise ValidationError(_('Only JPEG, PNG, WebP, and GIF images are allowed.'))
            max_bytes = self.MAX_SIZE_MB * 1024 * 1024
            if value.size > max_bytes:
                raise ValidationError(
                    _('Image size must be no more than %(size)sMB.'),
                    params={'size': self.MAX_SIZE_MB}
                )


class ProductNameValidator:
    MIN_LENGTH = 3
    MAX_LENGTH = 500

    def __call__(self, value):
        if len(value) < self.MIN_LENGTH:
            raise ValidationError(
                _('Product name must be at least %(min)d characters.'),
                params={'min': self.MIN_LENGTH}
            )
        if len(value) > self.MAX_LENGTH:
            raise ValidationError(
                _('Product name cannot exceed %(max)d characters.'),
                params={'max': self.MAX_LENGTH}
            )


class BarcodeValidator:
    def __call__(self, value):
        if not value:
            return
        clean = re.sub(r'[\s\-]', '', value)
        if not clean.isdigit():
            raise ValidationError(_('Barcode must contain only digits.'))
        if len(clean) not in (8, 12, 13, 14):
            raise ValidationError(_('Barcode must be 8, 12, 13, or 14 digits long.'))
