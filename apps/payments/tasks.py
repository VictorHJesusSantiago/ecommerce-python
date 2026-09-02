from celery import shared_task
from django.utils import timezone
from datetime import timedelta


@shared_task
def reconcile_payments():
    from .models import Transaction
    pending = Transaction.objects.filter(
        status='processing',
        created_at__lt=timezone.now() - timedelta(hours=1)
    )
    count = 0
    for txn in pending:
        txn.fail(error_message='Payment timed out')
        count += 1
    return count


@shared_task
def generate_payment_report():
    from .models import Transaction
    from django.db.models import Sum, Count
    today = timezone.now().date()
    stats = Transaction.objects.filter(
        created_at__date=today,
        status='completed'
    ).aggregate(
        count=Count('id'),
        total=Sum('amount'),
        fees=Sum('fee'),
    )
    return stats
