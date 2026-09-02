from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order, OrderItem
from apps.common.signals import order_completed


@receiver(post_save, sender=Order)
def order_post_save(sender, instance, created, **kwargs):
    if created:
        instance.user.total_orders += 1
        instance.user.save(update_fields=['total_orders', 'updated_at'])


@receiver(order_completed)
def handle_order_completed(sender, order, **kwargs):
    for item in order.items.all():
        item.product.increment_sold_count(item.quantity)

    order.user.total_spent += order.total
    order.user.save(update_fields=['total_spent', 'updated_at'])

    points = int(order.total)
    order.user.add_loyalty_points(points)

    from apps.notifications.tasks import send_order_confirmation_email
    send_order_confirmation_email.delay(str(order.id))
