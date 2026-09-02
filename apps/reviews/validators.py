from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class ReviewBodyValidator:
    MIN_LENGTH = 10
    MAX_LENGTH = 10000

    def __call__(self, value):
        if len(value) < self.MIN_LENGTH:
            raise ValidationError(
                _('Review must be at least %(min)d characters.'),
                params={'min': self.MIN_LENGTH}
            )
        if len(value) > self.MAX_LENGTH:
            raise ValidationError(
                _('Review cannot exceed %(max)d characters.'),
                params={'max': self.MAX_LENGTH}
            )


class ReviewTitleValidator:
    def __call__(self, value):
        if value and len(value) > 200:
            raise ValidationError(_('Review title cannot exceed 200 characters.'))


class ReviewImageValidator:
    ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp']
    MAX_SIZE_MB = 5

    def __call__(self, value):
        if hasattr(value, 'content_type'):
            if value.content_type not in self.ALLOWED_TYPES:
                raise ValidationError(_('Only JPEG, PNG, and WebP images are allowed.'))
            max_bytes = self.MAX_SIZE_MB * 1024 * 1024
            if value.size > max_bytes:
                raise ValidationError(
                    _('Image size must be no more than %(size)sMB.'),
                    params={'size': self.MAX_SIZE_MB}
                )
