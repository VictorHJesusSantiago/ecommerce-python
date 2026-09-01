from celery import shared_task
from django.utils import timezone
from django.db.models import F


@shared_task
def check_low_stock():
    from .models import StockItem
    low_items = StockItem.objects.filter(
        quantity__lte=F('low_stock_threshold'),
        product__is_active=True
    ).select_related('product', 'warehouse')

    for item in low_items:
        from apps.common.signals import inventory_low_stock
        inventory_low_stock.send(
            sender=StockItem,
            product=item.product,
            current_stock=item.quantity
        )

    return low_items.count()


@shared_task
def sync_inventory_levels():
    from apps.products.models import Product
    from .models import StockItem
    products = Product.objects.filter(track_inventory=True, is_active=True)
    updated = 0
    for product in products:
        total_stock = StockItem.objects.filter(product=product).aggregate(
            total=F('quantity')
        )['total'] or 0
        if product.quantity != total_stock:
            product.quantity = total_stock
            product.save(update_fields=['quantity', 'updated_at'])
            updated += 1
    return updated


@shared_task
def generate_inventory_report():
    from .models import StockItem, Warehouse
    from django.db.models import Sum
    warehouses = Warehouse.objects.filter(is_active=True)
    report = []
    for warehouse in warehouses:
        items = StockItem.objects.filter(warehouse=warehouse)
        total_value = items.aggregate(value=Sum(F('quantity') * F('cost_price')))['value'] or 0
        report.append({
            'warehouse': warehouse.name,
            'total_items': items.count(),
            'total_quantity': items.aggregate(qty=Sum('quantity'))['qty'] or 0,
            'total_value': str(total_value),
            'low_stock_count': items.filter(quantity__lte=F('low_stock_threshold')).count(),
        })
    return report


@shared_task
def cleanup_old_stock_movements():
    from .models import StockMovement
    from datetime import timedelta
    threshold = timezone.now() - timedelta(days=365)
    deleted, _ = StockMovement.objects.filter(created_at__lt=threshold).delete()
    return deleted
