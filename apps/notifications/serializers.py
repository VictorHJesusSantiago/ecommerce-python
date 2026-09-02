from rest_framework import serializers
from .models import (
    Notification, EmailTemplate, NotificationPreference,
    SMSLog, PushNotificationLog
)


class NotificationSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'type_display', 'priority', 'priority_display',
            'title', 'message', 'data', 'is_read', 'read_at', 'action_url',
            'icon', 'created_at',
        ]
        read_only_fields = ['id', 'read_at', 'created_at']


class NotificationListSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_notification_type_display', read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'notification_type', 'type_display', 'title', 'is_read', 'created_at']


class EmailTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailTemplate
        fields = ['id', 'name', 'subject', 'template_file', 'is_active',
                  'description', 'variables', 'created_at']
        read_only_fields = ['id', 'created_at']


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = [
            'id', 'email_order_updates', 'email_shipping_updates',
            'email_promotions', 'email_newsletter', 'email_review_reminders',
            'email_cart_reminders', 'push_order_updates', 'push_shipping_updates',
            'push_promotions', 'sms_order_updates', 'sms_shipping_updates',
        ]


class SMSLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SMSLog
        fields = ['id', 'phone_number', 'message', 'status', 'cost', 'created_at']
        read_only_fields = fields


class PushNotificationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = PushNotificationLog
        fields = ['id', 'title', 'body', 'data', 'status', 'created_at']
        read_only_fields = fields
