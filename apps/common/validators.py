import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from decimal import Decimal


class PhoneNumberValidator:
    def __init__(self, message=None):
        self.message = message or _('Enter a valid phone number.')

    def __call__(self, value):
        pattern = re.compile(r'^\+?1?\d{9,15}$')
        if not pattern.match(value):
            raise ValidationError(self.message)

    def deconstruct(self):
        return ('apps.common.validators.PhoneNumberValidator', [], {'message': self.message})


class StrongPasswordValidator:
    def __init__(self, min_length=8):
        self.min_length = min_length

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                _('Password must be at least %(min_length)d characters long.'),
                code='password_too_short',
                params={'min_length': self.min_length},
            )
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _('Password must contain at least one uppercase letter.'),
                code='password_no_uppercase',
            )
        if not re.search(r'[a-z]', password):
            raise ValidationError(
                _('Password must contain at least one lowercase letter.'),
                code='password_no_lowercase',
            )
        if not re.search(r'\d', password):
            raise ValidationError(
                _('Password must contain at least one digit.'),
                code='password_no_digit',
            )
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(
                _('Password must contain at least one special character.'),
                code='password_no_special',
            )

    def get_help_text(self):
        return _(
            'Your password must contain at least %(min_length)d characters, '
            'including uppercase, lowercase, digit, and special characters.'
        ) % {'min_length': self.min_length}


class NoSpecialCharactersValidator:
    def __init__(self, message=None, allowed='_- '):
        self.message = message or _('Field contains invalid characters.')
        self.allowed = allowed

    def __call__(self, value):
        for char in value:
            if not char.isalnum() and char not in self.allowed:
                raise ValidationError(self.message)


class PriceValidator:
    def __init__(self, min_value=Decimal('0.01'), max_value=Decimal('999999.99')):
        self.min_value = min_value
        self.max_value = max_value

    def __call__(self, value):
        if value < self.min_value:
            raise ValidationError(
                _('Price must be at least %(min)s.'),
                params={'min': self.min_value}
            )
        if value > self.max_value:
            raise ValidationError(
                _('Price cannot exceed %(max)s.'),
                params={'max': self.max_value}
            )


class DiscountPercentValidator:
    def __call__(self, value):
        if value < 0 or value > 100:
            raise ValidationError(_('Discount percentage must be between 0 and 100.'))


class ImageSizeValidator:
    def __init__(self, max_size_mb=5):
        self.max_size_mb = max_size_mb

    def __call__(self, file):
        if hasattr(file, 'size'):
            max_bytes = self.max_size_mb * 1024 * 1024
            if file.size > max_bytes:
                raise ValidationError(
                    _('Image file size must be no more than %(size)sMB.'),
                    params={'size': self.max_size_mb}
                )


class SlugValidator:
    def __init__(self, allow_unicode=False):
        self.allow_unicode = allow_unicode

    def __call__(self, value):
        if self.allow_unicode:
            pattern = re.compile(r'^[-\w]+$', re.UNICODE)
        else:
            pattern = re.compile(r'^[-\w]+$')
        if not pattern.match(value):
            raise ValidationError(_('Enter a valid slug.'))


class QuantityValidator:
    def __init__(self, min_value=0, max_value=99999):
        self.min_value = min_value
        self.max_value = max_value

    def __call__(self, value):
        if value < self.min_value:
            raise ValidationError(
                _('Quantity must be at least %(min)d.'),
                params={'min': self.min_value}
            )
        if value > self.max_value:
            raise ValidationError(
                _('Quantity cannot exceed %(max)d.'),
                params={'max': self.max_value}
            )


class SKUValidator:
    def __call__(self, value):
        pattern = re.compile(r'^[A-Z0-9]{2,20}$')
        if not pattern.match(value):
            raise ValidationError(
                _('SKU must be 2-20 uppercase alphanumeric characters.')
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
