from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class NotificationTitleValidator:
    def __call__(self, value):
        if len(value) > 200:
            raise ValidationError(_('Notification title cannot exceed 200 characters.'))
        if len(value) < 3:
            raise ValidationError(_('Notification title must be at least 3 characters.'))


class DeviceTokenValidator:
    def __call__(self, value):
        if value and len(value) < 10:
            raise ValidationError(_('Invalid device token.'))
