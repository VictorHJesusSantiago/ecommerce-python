from celery import shared_task
from django.utils import timezone
from datetime import timedelta


@shared_task
def generate_report(report_id):
    from .models import Report
    from django.db.models import Sum, Count
    try:
        report = Report.objects.get(pk=report_id)
        report.status = 'generating'
        report.save(update_fields=['status'])

        from apps.orders.models import Order
        from apps.products.models import Product
        from apps.users.models import User

        date_from = report.date_from or (timezone.now().date() - timedelta(days=30))
        date_to = report.date_to or timezone.now().date()

        orders = Order.objects.filter(
            created_at__date__gte=date_from,
            created_at__date__lte=date_to
        )

        data = {
            'summary': {
                'total_orders': orders.count(),
                'total_revenue': str(orders.filter(payment_status='paid').aggregate(total=Sum('total'))['total'] or 0),
                'average_order_value': str(orders.filter(payment_status='paid').aggregate(avg=Avg('total'))['avg'] or 0),
                'total_customers': orders.values('user').distinct().count(),
            },
            'by_status': list(
                orders.values('status').annotate(count=Count('id'))
            ),
            'by_date': list(
                orders.extra(select={'date': "date(created_at)"})
                .values('date')
                .annotate(count=Count('id'), revenue=Sum('total'))
            ),
        }

        report.data = data
        report.status = 'completed'
        from django.utils import timezone as tz
        report.completed_at = tz.now()
        report.save(update_fields=['data', 'status', 'completed_at', 'updated_at'])

    except Exception as e:
        report.status = 'failed'
        report.error_message = str(e)
        report.save(update_fields=['status', 'error_message', 'updated_at'])


@shared_task
def generate_daily_sales_report():
    from .models import DailyStats
    from apps.orders.models import Order
    from apps.users.models import User

    today = timezone.now().date()
    orders = Order.objects.filter(created_at__date=today)

    stats, _ = DailyStats.objects.get_or_create(date=today)
    stats.total_orders = orders.count()
    stats.total_revenue = orders.filter(payment_status='paid').aggregate(
        total=Sum('total')
    )['total'] or 0
    if stats.total_orders > 0:
        stats.average_order_value = stats.total_revenue / stats.total_orders
    stats.new_customers = User.objects.filter(created_at__date=today, role='customer').count()
    stats.refund_count = orders.filter(status='refunded').count()
    stats.refund_amount = orders.filter(status='refunded').aggregate(
        total=Sum('total')
    )['total'] or 0
    stats.save()


@shared_task
def generate_monthly_analytics():
    from .models import DailyStats
    from django.db.models import Sum, Count, Avg
    today = timezone.now().date()
    month_start = today.replace(day=1)
    stats = DailyStats.objects.filter(date__gte=month_start)
    return {
        'month': str(month_start),
        'total_orders': stats.aggregate(t=Sum('total_orders'))['t'] or 0,
        'total_revenue': str(stats.aggregate(t=Sum('total_revenue'))['t'] or 0),
    }
