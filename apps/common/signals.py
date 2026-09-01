from django.db.models.signals import pre_save, post_save, pre_delete, post_delete
from django.dispatch import Signal
from django.utils.text import slugify

order_completed = Signal()  # providing args: order
payment_received = Signal()  # providing args: payment, order
product_stock_changed = Signal()  # providing args: product, old_stock, new_stock
user_registered = Signal()  # providing args: user
review_created = Signal()  # providing args: review, product
coupon_used = Signal()  # providing args: coupon, user, order
cart_updated = Signal()  # providing args: cart, item
wishlist_item_added = Signal()  # providing args: wishlist_item
wishlist_item_removed = Signal()  # providing args: wishlist_item
refund_requested = Signal()  # providing args: refund, order
refund_approved = Signal()  # providing args: refund, order
notification_created = Signal()  # providing args: notification
inventory_low_stock = Signal()  # providing args: product, current_stock
shipment_updated = Signal()  # providing args: shipment, status
banner_impression = Signal()  # providing args: banner, user
newsletter_subscribed = Signal()  # providing args: subscriber
report_generated = Signal()  # providing args: report, report_type


def auto_slug_generator(sender, instance, **kwargs):
    if hasattr(instance, 'name') and not instance.slug:
        instance.slug = slugify(instance.name)


def log_model_change(sender, instance, created, **kwargs):
    import logging
    logger = logging.getLogger('apps.common')
    action = 'Created' if created else 'Updated'
    logger.info(f"{action} {sender.__name__} instance: {instance.pk}")
