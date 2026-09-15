import pytest
from apps.reports.models import Report, DailyStats


@pytest.mark.django_db
class TestReportModel:
    def test_report_creation(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        admin = User.objects.create_superuser(email='admin@test.com', password='pass')
        report = Report.objects.create(
            name='Monthly Sales',
            report_type='sales',
            generated_by=admin,
        )
        assert report.status == 'pending'


@pytest.mark.django_db
class TestDailyStats:
    def test_daily_stats(self):
        from django.utils import timezone
        stats = DailyStats.objects.create(
            date=timezone.now().date(),
            total_orders=10,
            total_revenue=1000,
            new_customers=5,
        )
        assert stats.total_orders == 10
