from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Review
from apps.common.signals import review_created


@receiver(review_created)
def handle_review_created(sender, review, product, **kwargs):
    from apps.notifications.tasks import send_notification
    if product.vendor:
        send_notification.delay(
            user_id=product.vendor.id,
            notification_type='review',
            title=f'New review for {product.name}',
            message=f'{review.user.email} left a {review.rating}-star review.',
            data={'product_id': str(product.id), 'review_id': str(review.id)},
        )


@receiver(post_save, sender=Review)
def review_post_save(sender, instance, **kwargs):
    if instance.is_approved:
        instance.product.update_rating()
