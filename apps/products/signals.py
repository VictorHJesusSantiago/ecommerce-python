from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Product, ProductImage, Category
from apps.common.signals import product_stock_changed


@receiver(post_save, sender=Product)
def product_post_save(sender, instance, created, **kwargs):
    if hasattr(instance, 'category') and instance.category:
        instance.category.update_product_count()
    from django.core.cache import cache
    cache.delete(f'product_{instance.pk}')
    cache.delete('featured_products')


@receiver(post_delete, sender=Product)
def product_post_delete(sender, instance, **kwargs):
    if hasattr(instance, 'category') and instance.category:
        instance.category.update_product_count()
    from django.core.cache import cache
    cache.delete(f'product_{instance.pk}')
    cache.delete('featured_products')


@receiver(post_delete, sender=ProductImage)
def product_image_delete(sender, instance, **kwargs):
    if instance.image:
        instance.image.delete(save=False)


@receiver(post_save, sender=Category)
def category_post_save(sender, instance, **kwargs):
    from django.core.cache import cache
    cache.delete('category_tree')


@receiver(post_save, sender=Product)
def check_low_stock_signal(sender, instance, **kwargs):
    if instance.track_inventory and instance.quantity <= instance.low_stock_threshold:
        product_stock_changed.send(
            sender=Product,
            product=instance,
            old_stock=instance.quantity + 10,
            new_stock=instance.quantity
        )
