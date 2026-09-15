import pytest
from celery import Celery


@pytest.mark.django_db
class TestCeleryTasks:
    def test_send_abandoned_cart_reminders(self):
        from apps.cart.tasks import send_abandoned_cart_reminders
        result = send_abandoned_cart_reminders.delay()
        assert result is not None

    def test_check_low_stock(self):
        from apps.inventory.tasks import check_low_stock
        result = check_low_stock.delay()
        assert result is not None

    def test_generate_daily_sales_report(self):
        from apps.reports.tasks import generate_daily_sales_report
        result = generate_daily_sales_report.delay()
        assert result is not None

    def test_cleanup_expired_coupons(self):
        from apps.marketing.tasks import cleanup_expired_coupons
        result = cleanup_expired_coupons.delay()
        assert result is not None
