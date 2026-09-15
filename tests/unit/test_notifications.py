import pytest
from apps.notifications.models import Notification, NotificationPreference


@pytest.mark.django_db
class TestNotificationModel:
    def test_notification_creation(self, user):
        notification = Notification.create_notification(
            user=user,
            notification_type='order',
            title='Order Confirmed',
            message='Your order has been confirmed.',
        )
        assert notification.is_read is False

    def test_mark_as_read(self, user):
        notification = Notification.create_notification(
            user=user,
            notification_type='system',
            title='Test',
            message='Test notification',
        )
        notification.mark_as_read()
        assert notification.is_read is True
        assert notification.read_at is not None


@pytest.mark.django_db
class TestNotificationPreference:
    def test_default_preferences(self, user):
        pref, created = NotificationPreference.objects.get_or_create(user=user)
        assert pref.email_order_updates is True
        assert pref.email_promotions is True
