import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class EmailDomainValidator:
    ALLOWED_DOMAINS = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 'aol.com']

    def __call__(self, value):
        domain = value.split('@')[-1].lower()
        if domain not in self.ALLOWED_DOMAINS:
            raise ValidationError(
                _('Email domain %(domain)s is not allowed.'),
                params={'domain': domain}
            )


class PhoneNumberValidator:
    def __init__(self, message=None):
        self.message = message or _('Enter a valid phone number.')

    def __call__(self, value):
        pattern = re.compile(r'^\+?1?\d{9,15}$')
        if not pattern.match(value):
            raise ValidationError(self.message)


class NoDisposableEmailValidator:
    DISPOSABLE_DOMAINS = ['tempmail.com', 'throwaway.com', 'guerrillamail.com']

    def __call__(self, value):
        domain = value.split('@')[-1].lower()
        if domain in self.DISPOSABLE_DOMAINS:
            raise ValidationError(_('Disposable email addresses are not allowed.'))


class UsernameValidator:
    def __call__(self, value):
        if len(value) < 3:
            raise ValidationError(_('Username must be at least 3 characters.'))
        if len(value) > 30:
            raise ValidationError(_('Username must be at most 30 characters.'))
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise ValidationError(_('Username can only contain letters, numbers, and underscores.'))
        reserved = ['admin', 'root', 'superuser', 'system', 'support', 'help']
        if value.lower() in reserved:
            raise ValidationError(_('This username is reserved.'))


class ProfileImageValidator:
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
