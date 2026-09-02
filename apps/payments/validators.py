from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re


class CardNumberValidator:
    def __call__(self, value):
        clean = re.sub(r'[\s\-]', '', value)
        if not clean.isdigit():
            raise ValidationError(_('Card number must contain only digits.'))
        if len(clean) < 13 or len(clean) > 19:
            raise ValidationError(_('Card number must be 13-19 digits.'))
        if not self._luhn_check(clean):
            raise ValidationError(_('Invalid card number.'))

    def _luhn_check(self, number):
        total = 0
        reverse = number[::-1]
        for i, digit in enumerate(reverse):
            n = int(digit)
            if i % 2 == 1:
                n *= 2
                if n > 9:
                    n -= 9
            total += n
        return total % 10 == 0


class ExpiryDateValidator:
    def __call__(self, month, year):
        from django.utils import timezone
        now = timezone.now()
        if year < now.year:
            raise ValidationError(_('Card has expired.'))
        if year == now.year and month < now.month:
            raise ValidationError(_('Card has expired.'))
        if month < 1 or month > 12:
            raise ValidationError(_('Invalid month.'))
