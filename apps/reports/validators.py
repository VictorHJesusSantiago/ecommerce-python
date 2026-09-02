from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class DateRangeValidator:
    def __call__(self, date_from, date_to):
        if date_from and date_to:
            if date_from > date_to:
                raise ValidationError(_('Start date must be before end date.'))
        if date_to and date_to > timezone.now().date():
            raise ValidationError(_('End date cannot be in the future.'))
