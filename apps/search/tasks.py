from celery import shared_task


@shared_task
def update_search_index():
    from apps.products.models import Product
    from django.db.models import Q
    count = Product.objects.filter(
        is_active=True, status='active'
    ).count()
    return count


@shared_task
def cleanup_old_search_queries():
    from .models import SearchQuery
    from django.utils import timezone
    from datetime import timedelta
    threshold = timezone.now() - timedelta(days=90)
    deleted, _ = SearchQuery.objects.filter(created_at__lt=threshold).delete()
    return deleted
