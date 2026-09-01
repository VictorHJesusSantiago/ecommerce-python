from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class PageSlugValidator:
    def __call__(self, value):
        import re
        if not re.match(r'^[-a-zA-Z0-9_]+$', value):
            raise ValidationError(_('Page slug can only contain letters, numbers, hyphens, and underscores.'))


class ContentLengthValidator:
    def __init__(self, min_length=10, max_length=100000):
        self.min_length = min_length
        self.max_length = max_length

    def __call__(self, value):
        if len(value) < self.min_length:
            raise ValidationError(
                _('Content must be at least %(min)d characters.'),
                params={'min': self.min_length}
            )
        if len(value) > self.max_length:
            raise ValidationError(
                _('Content cannot exceed %(max)d characters.'),
                params={'max': self.max_length}
            )
