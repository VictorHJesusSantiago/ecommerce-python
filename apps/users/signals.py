from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.core.cache import cache

User = get_user_model()


@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    if created:
        from apps.users.models import UserActivity
        UserActivity.log(instance, 'login', 'Account created')
    cache.delete(f'user_{instance.pk}')


@receiver(post_save, sender=User)
def invalidate_user_cache(sender, instance, **kwargs):
    cache.delete(f'user_{instance.pk}')
    cache.delete(f'user_profile_{instance.pk}')
