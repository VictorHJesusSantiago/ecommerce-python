from celery import shared_task
from django.utils import timezone
from datetime import timedelta


@shared_task
def send_abandoned_cart_reminders():
    from .models import Cart
    from apps.common.utils import send_templated_email
    threshold = timezone.now() - timedelta(hours=24)
    abandoned_carts = Cart.objects.filter(
        is_active=True,
        updated_at__lt=threshold,
        user__isnull=False,
        user__is_active=True,
    ).select_related('user').prefetch_related('items')

    count = 0
    for cart in abandoned_carts:
        if cart.items.exists():
            try:
                send_templated_email(
                    subject='You left items in your cart!',
                    template_name='emails/abandoned_cart.html',
                    context={
                        'user': cart.user,
                        'cart': cart,
                        'items': cart.items.all()[:5],
                        'cart_total': cart.subtotal,
                    },
                    recipient_list=[cart.user.email],
                )
                count += 1
            except Exception:
                continue
    return count


@shared_task
def cleanup_old_carts():
    from .models import Cart
    threshold = timezone.now() - timedelta(days=90)
    deleted, _ = Cart.objects.filter(
        is_active=False, updated_at__lt=threshold
    ).delete()
    return deleted


@shared_task
def merge_anonymous_cart(session_key, user_id):
    from .models import Cart, CartItem
    from django.contrib.auth import get_user_model
    User = get_user_model()
    try:
        anon_cart = Cart.objects.get(session_key=session_key, is_active=True)
        user_cart, _ = Cart.objects.get_or_create(user_id=user_id, is_active=True)
        for item in anon_cart.items.all():
            existing = CartItem.objects.filter(
                cart=user_cart, product=item.product, variant=item.variant
            ).first()
            if existing:
                existing.quantity += item.quantity
                existing.save(update_fields=['quantity'])
            else:
                item.cart = user_cart
                item.save(update_fields=['cart'])
        anon_cart.is_active = False
        anon_cart.save(update_fields=['is_active'])
        return True
    except Exception:
        return False


@shared_task
def cleanup_expired_cart_items():
    from .models import Cart
    threshold = timezone.now() - timedelta(days=30)
    carts = Cart.objects.filter(
        is_active=True, updated_at__lt=threshold
    )
    updated = 0
    for cart in carts:
        cart.is_active = False
        cart.save(update_fields=['is_active'])
        updated += 1
    return updated
