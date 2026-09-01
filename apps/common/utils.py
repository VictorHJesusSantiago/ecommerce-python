import hashlib
import shortuuid
import qrcode
import io
import base64
import secrets
import string
from decimal import Decimal
from django.utils.text import slugify
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string


def generate_unique_code(length=8):
    return shortuuid.ShortUUID().random(length=length).upper()


def generate_order_number():
    prefix = timezone.now().strftime('%Y%m%d')
    random_part = generate_unique_code(6)
    return f"ORD-{prefix}-{random_part}"


def generate_sku(product_id, variant_id=None):
    base = f"SKU-{product_id:06d}"
    if variant_id:
        base = f"{base}-V{variant_id:03d}"
    return base


def generate_tracking_number():
    return f"TRK-{generate_unique_code(12)}"


def generate_refund_number():
    return f"REF-{generate_unique_code(8)}"


def generate_transaction_id():
    return f"TXN-{generate_unique_code(16)}"


def generate_coupon_code(length=10):
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))


def format_currency(amount, currency='USD'):
    symbols = {
        'USD': '$', 'EUR': '€', 'GBP': '£', 'JPY': '¥',
        'CAD': 'C$', 'AUD': 'A$', 'BRL': 'R$',
    }
    symbol = symbols.get(currency, currency + ' ')
    if currency == 'JPY':
        return f"{symbol}{int(amount):,}"
    return f"{symbol}{Decimal(str(amount)):,.2f}"


def calculate_discount(original_price, discount_amount=None, discount_percent=None):
    if discount_percent:
        discount = original_price * (discount_percent / Decimal('100'))
    elif discount_amount:
        discount = min(discount_amount, original_price)
    else:
        return Decimal('0'), original_price
    final_price = original_price - discount
    return discount, final_price


def generate_qr_code(data, size=200):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode()


def send_templated_email(subject, template_name, context, recipient_list, from_email=None):
    if from_email is None:
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@ecommerce.com')
    html_content = render_to_string(template_name, context)
    text_content = render_to_string(template_name.replace('.html', '.txt'), context)
    msg = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
    msg.attach_alternative(html_content, "text/html")
    return msg.send(fail_silently=False)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def cache_key(*args):
    return ':'.join(str(a) for a in args)


def cache_result(timeout=300, key_prefix=''):
    def decorator(func):
        def wrapper(*args, **kwargs):
            key_parts = [key_prefix or func.__module__, func.__name__]
            key_parts.extend([str(a) for a in args])
            key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
            full_key = cache_key(*key_parts)
            result = cache.get(full_key)
            if result is None:
                result = func(*args, **kwargs)
                cache.set(full_key, result, timeout)
            return result
        return wrapper
    return decorator


def paginate_queryset(queryset, page, page_size=20):
    from django.core.paginator import Paginator, EmptyPage
    paginator = Paginator(queryset, page_size)
    try:
        items = paginator.page(page)
    except EmptyPage:
        items = paginator.page(paginator.num_pages)
    return {
        'items': items.object_list,
        'page': items.number,
        'pages': paginator.num_pages,
        'total': paginator.count,
        'has_next': items.has_next(),
        'has_previous': items.has_previous(),
    }


def chunk_list(lst, size):
    return [lst[i:i + size] for i in range(0, len(lst), size)]


def mask_email(email):
    if '@' not in email:
        return email
    local, domain = email.split('@')
    if len(local) <= 2:
        masked = local[0] + '*' * (len(local) - 1)
    else:
        masked = local[:2] + '*' * (len(local) - 2)
    return f"{masked}@{domain}"


def mask_phone(phone):
    if len(phone) <= 4:
        return phone
    return '*' * (len(phone) - 4) + phone[-4:]


def calculate_shipping_weight(items):
    total = Decimal('0')
    for item in items:
        if hasattr(item, 'product') and hasattr(item.product, 'weight'):
            total += item.product.weight * item.quantity
    return total
