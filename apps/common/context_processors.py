from django.conf import settings
from .models import SiteSettings


def site_settings(request):
    try:
        site = SiteSettings.objects.first()
        return {
            'site_name': site.site_name if site else 'E-Commerce Store',
            'site_tagline': site.tagline if site else '',
            'currency': site.currency if site else 'USD',
        }
    except Exception:
        return {
            'site_name': 'E-Commerce Store',
            'site_tagline': '',
            'currency': 'USD',
        }


def cart_context(request):
    context = {
        'cart_count': 0,
        'cart_total': 0,
    }
    if hasattr(request, 'user') and request.user.is_authenticated:
        from apps.cart.models import Cart
        try:
            cart = Cart.objects.filter(user=request.user, is_active=True).first()
            if cart:
                context['cart_count'] = cart.items.count()
                context['cart_total'] = cart.subtotal
        except Exception:
            pass
    elif request.session.session_key:
        from apps.cart.models import Cart
        try:
            cart = Cart.objects.filter(
                session_key=request.session.session_key,
                is_active=True
            ).first()
            if cart:
                context['cart_count'] = cart.items.count()
                context['cart_total'] = cart.subtotal
        except Exception:
            pass
    return context


def notification_context(request):
    context = {
        'unread_notifications': 0,
    }
    if hasattr(request, 'user') and request.user.is_authenticated:
        from apps.notifications.models import Notification
        try:
            context['unread_notifications'] = Notification.objects.filter(
                user=request.user,
                is_read=False
            ).count()
        except Exception:
            pass
    return context
