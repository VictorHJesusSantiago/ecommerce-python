from celery import shared_task
from django.utils import timezone
from datetime import timedelta


@shared_task
def send_order_confirmation_email(order_id):
    from .models import Order
    from apps.common.utils import send_templated_email
    try:
        order = Order.objects.get(pk=order_id)
        send_templated_email(
            subject=f'Order Confirmation - {order.order_number}',
            template_name='emails/order_confirmation.html',
            context={'order': order, 'items': order.items.all()},
            recipient_list=[order.user.email],
        )
    except Order.DoesNotExist:
        pass


@shared_task
def send_shipping_notification(order_id, shipment_id):
    from .models import Order, Shipment
    from apps.common.utils import send_templated_email
    try:
        order = Order.objects.get(pk=order_id)
        shipment = Shipment.objects.get(pk=shipment_id)
        send_templated_email(
            subject=f'Your Order {order.order_number} Has Shipped!',
            template_name='emails/shipping_notification.html',
            context={'order': order, 'shipment': shipment},
            recipient_list=[order.user.email],
        )
    except (Order.DoesNotExist, Shipment.DoesNotExist):
        pass


@shared_task
def send_delivery_confirmation(order_id):
    from .models import Order
    from apps.common.utils import send_templated_email
    try:
        order = Order.objects.get(pk=order_id)
        send_templated_email(
            subject=f'Order {order.order_number} Delivered',
            template_name='emails/delivery_confirmation.html',
            context={'order': order},
            recipient_list=[order.user.email],
        )
    except Order.DoesNotExist:
        pass


@shared_task
def auto_cancel_old_orders():
    from .models import Order
    threshold = timezone.now() - timedelta(days=3)
    orders = Order.objects.filter(
        status='pending', created_at__lt=threshold
    )
    count = 0
    for order in orders:
        order.cancel('Auto-cancelled: unpaid after 3 days')
        count += 1
    return count


@shared_task
def sync_order_status():
    from .models import Order
    from django.db.models import Q
    stuck_orders = Order.objects.filter(
        Q(status='processing', updated_at__lt=timezone.now() - timedelta(days=5)) |
        Q(status='shipped', updated_at__lt=timezone.now() - timedelta(days=30))
    )
    return stuck_orders.count()
