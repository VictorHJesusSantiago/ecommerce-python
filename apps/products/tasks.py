from celery import shared_task
from django.utils import timezone
from datetime import timedelta


@shared_task
def update_product_rating(product_id):
    from .models import Product
    try:
        product = Product.objects.get(pk=product_id)
        product.update_rating()
    except Product.DoesNotExist:
        pass


@shared_task
def generate_product_feed():
    from .models import Product
    import json
    products = Product.objects.filter(is_active=True, status='active').select_related('category', 'brand')
    feed_data = []
    for product in products:
        feed_data.append({
            'id': str(product.id),
            'title': product.name,
            'description': product.short_description or product.description[:500],
            'price': str(product.price),
            'currency': 'USD',
            'availability': 'in_stock' if product.is_in_stock else 'out_of_stock',
            'condition': 'new',
            'link': f'/products/{product.slug}/',
            'image_link': product.images.filter(is_primary=True).first().image.url if product.images.filter(is_primary=True).exists() else '',
            'brand': product.brand.name if product.brand else '',
            'category': product.category.name if product.category else '',
            'gtin': product.barcode or '',
            'mpn': product.sku,
        })
    return json.dumps(feed_data)


@shared_task
def sync_product_inventory():
    from .models import Product
    products = Product.objects.filter(track_inventory=True, is_active=True)
    low_stock = []
    for product in products:
        if product.quantity <= product.low_stock_threshold:
            low_stock.append({
                'product_id': str(product.id),
                'name': product.name,
                'quantity': product.quantity,
                'threshold': product.low_stock_threshold,
            })
    return low_stock


@shared_task
def cleanup_archived_products():
    from .models import Product
    threshold = timezone.now() - timedelta(days=365)
    count = Product.all_objects.filter(
        status='archived', updated_at__lt=threshold, is_deleted=False
    ).update(is_deleted=True)
    return count
