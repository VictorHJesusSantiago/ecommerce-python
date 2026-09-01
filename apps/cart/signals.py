from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Cart, CartItem
from apps.common.signals import cart_updated


@receiver(post_save, sender=CartItem)
def cart_item_post_save(sender, instance, created, **kwargs):
    instance.cart.save(update_fields=['updated_at'])


@receiver(post_delete, sender=CartItem)
def cart_item_post_delete(sender, instance, **kwargs):
    cart = instance.cart
    if cart.items.count() == 0:
        pass


@receiver(post_delete, sender=Cart)
def cart_post_delete(sender, instance, **kwargs):
    instance.items.all().delete()
