from django.contrib import admin
from .models import (
    Notification, EmailTemplate, NotificationPreference,
    SMSLog, PushNotificationLog
)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'priority', 'title', 'is_read', 'created_at']
    list_filter = ['notification_type', 'priority', 'is_read']
    search_fields = ['user__email', 'title', 'message']
    readonly_fields = ['read_at', 'created_at']


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'subject', 'template_file', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'subject']
    readonly_fields = ['created_at']


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'email_order_updates', 'email_shipping_updates',
                    'email_promotions', 'push_order_updates']
    search_fields = ['user__email']


@admin.register(SMSLog)
class SMSLogAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'status', 'cost', 'created_at']
    list_filter = ['status']
    readonly_fields = ['provider_response', 'created_at']


@admin.register(PushNotificationLog)
class PushNotificationLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'status', 'created_at']
    list_filter = ['status']
    readonly_fields = ['provider_response', 'created_at']
