import pytest
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from apps.marketing.models import Coupon, Banner, Newsletter


@pytest.mark.django_db
class TestCouponModel:
    def test_coupon_valid(self):
        from apps.marketing.models import Coupon
        coupon = Coupon.objects.create(
            code='TEST10',
            discount_type='percentage',
            discount_value=Decimal('10'),
            start_date=timezone.now() - timedelta(days=1),
            end_date=timezone.now() + timedelta(days=30),
            is_active=True,
        )
        assert coupon.is_valid is True

    def test_percentage_discount(self):
        from apps.marketing.models import Coupon
        coupon = Coupon.objects.create(
            code='SAVE20',
            discount_type='percentage',
            discount_value=Decimal('20'),
            start_date=timezone.now() - timedelta(days=1),
            end_date=timezone.now() + timedelta(days=30),
            is_active=True,
        )
        discount = coupon.calculate_discount(Decimal('100'))
        assert discount == Decimal('20.00')

    def test_fixed_discount(self):
        from apps.marketing.models import Coupon
        coupon = Coupon.objects.create(
            code='FLAT15',
            discount_type='fixed',
            discount_value=Decimal('15'),
            start_date=timezone.now() - timedelta(days=1),
            end_date=timezone.now() + timedelta(days=30),
            is_active=True,
        )
        discount = coupon.calculate_discount(Decimal('100'))
        assert discount == Decimal('15.00')


@pytest.mark.django_db
class TestBannerModel:
    def test_banner_creation(self):
        banner = Banner.objects.create(
            title='Summer Sale',
            image='test.jpg',
            is_active=True,
        )
        assert banner.title == 'Summer Sale'


@pytest.mark.django_db
class TestNewsletterModel:
    def test_newsletter_subscribe(self):
        subscriber = Newsletter.objects.create(
            email='test@example.com',
            source='website',
        )
        assert subscriber.is_active is True

    def test_newsletter_unsubscribe(self):
        subscriber = Newsletter.objects.create(
            email='test@example.com',
            source='website',
        )
        subscriber.unsubscribe()
        assert subscriber.is_active is False
