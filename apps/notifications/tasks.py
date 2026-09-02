from celery import shared_task
from django.utils import timezone


@shared_task
def send_notification(user_id, notification_type, title, message, **kwargs):
    from django.contrib.auth import get_user_model
    from .models import Notification
    User = get_user_model()
    try:
        user = User.objects.get(pk=user_id)
        Notification.create_notification(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            **kwargs
        )
        return True
    except User.DoesNotExist:
        return False


@shared_task
def send_order_confirmation_email(order_id):
    from apps.common.utils import send_templated_email
    from apps.orders.models import Order
    try:
        order = Order.objects.get(pk=order_id)
        send_templated_email(
            subject=f'Order Confirmation - {order.order_number}',
            template_name='emails/order_confirmation.html',
            context={'order': order, 'items': order.items.all()},
            recipient_list=[order.user.email],
        )
        Notification.create_notification(
            user=order.user,
            notification_type='order',
            title=f'Order {order.order_number} Confirmed',
            message=f'Your order {order.order_number} has been confirmed.',
            data={'order_id': str(order.id)},
            action_url=f'/orders/{order.order_number}/',
        )
        return True
    except Exception:
        return False


@shared_task
def send_shipping_update(order_id):
    from apps.common.utils import send_templated_email
    from apps.orders.models import Order
    try:
        order = Order.objects.get(pk=order_id)
        send_templated_email(
            subject=f'Shipping Update - Order {order.order_number}',
            template_name='emails/shipping_update.html',
            context={'order': order},
            recipient_list=[order.user.email],
        )
        Notification.create_notification(
            user=order.user,
            notification_type='shipping',
            title=f'Order {order.order_number} Shipped',
            message=f'Your order has been shipped. Tracking: {order.tracking_number}',
            data={'order_id': str(order.id)},
        )
        return True
    except Exception:
        return False


@shared_task
def send_password_reset_email(email):
    from apps.common.utils import send_templated_email, generate_unique_code
    from django.contrib.auth import get_user_model
    User = get_user_model()
    try:
        user = User.objects.get(email=email)
        code = generate_unique_code(32)
        send_templated_email(
            subject='Password Reset Request',
            template_name='emails/password_reset.html',
            context={'user': user, 'reset_code': code},
            recipient_list=[email],
        )
        return True
    except User.DoesNotExist:
        return False


@shared_task
def process_pending_notifications():
    from .models import Notification
    pending = Notification.objects.filter(is_read=False)
    return pending.count()


@shared_task
def send_sms(phone_number, message, user_id=None):
    from .models import SMSLog
    log = SMSLog.objects.create(
        user_id=user_id,
        phone_number=phone_number,
        message=message,
        status='sent',
    )
    return log.id


@shared_task
def send_push_notification(user_id, title, body, data=None):
    from django.contrib.auth import get_user_model
    from .models import PushNotificationLog, Notification
    User = get_user_model()
    try:
        user = User.objects.get(pk=user_id)
        log = PushNotificationLog.objects.create(
            user=user,
            title=title,
            body=body,
            data=data or {},
            status='sent',
        )
        Notification.create_notification(
            user=user,
            notification_type='system',
            title=title,
            message=body,
            data=data or {},
        )
        return log.id
    except User.DoesNotExist:
        return False
