from django.db import models
from django.conf import settings
from apps.common.models import TimeStampedModel, UUIDModel


class Notification(UUIDModel, TimeStampedModel):
    NOTIFICATION_TYPES = [
        ('order', 'Order'),
        ('payment', 'Payment'),
        ('shipping', 'Shipping'),
        ('promotion', 'Promotion'),
        ('system', 'System'),
        ('review', 'Review'),
        ('account', 'Account'),
        ('inventory', 'Inventory'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    title = models.CharField(max_length=200)
    message = models.TextField()
    data = models.JSONField(default=dict, blank=True)
    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)
    action_url = models.URLField(blank=True, default='')
    icon = models.CharField(max_length=50, blank=True, default='')

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['notification_type']),
        ]

    def __str__(self):
        return f"{self.title} for {self.user.email}"

    def mark_as_read(self):
        from django.utils import timezone
        self.is_read = True
        self.read_at = timezone.now()
        self.save(update_fields=['is_read', 'read_at', 'updated_at'])

    @classmethod
    def create_notification(cls, user, notification_type, title, message, **kwargs):
        return cls.objects.create(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            **kwargs
        )


class EmailTemplate(UUIDModel, TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    subject = models.CharField(max_length=200)
    template_file = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True, default='')
    variables = models.JSONField(default=list, blank=True)

    class Meta:
        verbose_name = 'Email Template'
        verbose_name_plural = 'Email Templates'
        ordering = ['name']

    def __str__(self):
        return self.name


class NotificationPreference(UUIDModel, TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='notification_preferences'
    )
    email_order_updates = models.BooleanField(default=True)
    email_shipping_updates = models.BooleanField(default=True)
    email_promotions = models.BooleanField(default=True)
    email_newsletter = models.BooleanField(default=True)
    email_review_reminders = models.BooleanField(default=True)
    email_cart_reminders = models.BooleanField(default=True)
    push_order_updates = models.BooleanField(default=True)
    push_shipping_updates = models.BooleanField(default=True)
    push_promotions = models.BooleanField(default=False)
    sms_order_updates = models.BooleanField(default=False)
    sms_shipping_updates = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Notification Preference'
        verbose_name_plural = 'Notification Preferences'

    def __str__(self):
        return f"Preferences for {self.user.email}"


class SMSLog(UUIDModel, TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    phone_number = models.CharField(max_length=20)
    message = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('sent', 'Sent'),
            ('delivered', 'Delivered'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )
    provider_response = models.JSONField(default=dict, blank=True)
    cost = models.DecimalField(max_digits=8, decimal_places=6, default=0)

    class Meta:
        verbose_name = 'SMS Log'
        verbose_name_plural = 'SMS Logs'
        ordering = ['-created_at']

    def __str__(self):
        return f"SMS to {self.phone_number} - {self.status}"


class PushNotificationLog(UUIDModel, TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='push_logs'
    )
    title = models.CharField(max_length=200)
    body = models.TextField()
    data = models.JSONField(default=dict, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('sent', 'Sent'),
            ('delivered', 'Delivered'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )
    device_token = models.CharField(max_length=500, blank=True, default='')
    provider_response = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = 'Push Notification Log'
        verbose_name_plural = 'Push Notification Logs'
        ordering = ['-created_at']

    def __str__(self):
        return f"Push to {self.user.email} - {self.status}"
