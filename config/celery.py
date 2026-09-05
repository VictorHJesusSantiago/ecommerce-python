import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
app = Celery('ecommerce')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'check-low-stock-every-hour': {
        'task': 'apps.inventory.tasks.check_low_stock',
        'schedule': crontab(minute=0, hour='*/1'),
    },
    'send-pending-notifications-every-5-mins': {
        'task': 'apps.notifications.tasks.process_pending_notifications',
        'schedule': crontab(minute='*/5'),
    },
    'generate-daily-sales-report': {
        'task': 'apps.reports.tasks.generate_daily_sales_report',
        'schedule': crontab(minute=0, hour=1),
    },
    'cleanup-expired-coupons-daily': {
        'task': 'apps.marketing.tasks.cleanup_expired_coupons',
        'schedule': crontab(minute=0, hour=2),
    },
    'update-search-index-every-30-mins': {
        'task': 'apps.search.tasks.update_search_index',
        'schedule': crontab(minute='*/30'),
    },
    'sync-inventory-every-15-mins': {
        'task': 'apps.inventory.tasks.sync_inventory_levels',
        'schedule': crontab(minute='*/15'),
    },
    'send-abandoned-cart-emails': {
        'task': 'apps.cart.tasks.send_abandoned_cart_reminders',
        'schedule': crontab(minute=0, hour='*/6'),
    },
    'generate-monthly-analytics': {
        'task': 'apps.reports.tasks.generate_monthly_analytics',
        'schedule': crontab(minute=0, hour=3, day_of_month=1),
    },
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
