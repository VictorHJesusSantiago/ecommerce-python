from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class SearchQueryValidator:
    MAX_LENGTH = 500
    MIN_LENGTH = 2

    def __call__(self, value):
        if len(value) < self.MIN_LENGTH:
            raise ValidationError(_('Search query must be at least 2 characters.'))
        if len(value) > self.MAX_LENGTH:
            raise ValidationError(_('Search query cannot exceed 500 characters.'))

    def sanitize(self, value):
        import re
        value = re.sub(r'[^\w\s\-]', '', value)
        value = re.sub(r'\s+', ' ', value).strip()
        return value[:self.MAX_LENGTH]


class SearchFilterValidator:
    def validate_price_range(self, min_price, max_price):
        if min_price is not None and max_price is not None:
            if min_price > max_price:
                raise ValidationError(_('Minimum price cannot be greater than maximum price.'))
        if min_price is not None and min_price < 0:
            raise ValidationError(_('Minimum price cannot be negative.'))
        if max_price is not None and max_price < 0:
            raise ValidationError(_('Maximum price cannot be negative.'))
