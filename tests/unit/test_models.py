import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    def test_create_user(self):
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPass123!'
        )
        assert user.email == 'test@example.com'
        assert user.is_active is True
        assert user.check_password('TestPass123!')

    def test_create_superuser(self):
        admin = User.objects.create_superuser(
            email='admin@example.com',
            username='admin',
            password='AdminPass123!'
        )
        assert admin.is_staff is True
        assert admin.is_superuser is True

    def test_user_full_name(self):
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPass123!',
            first_name='John',
            last_name='Doe'
        )
        assert user.full_name == 'John Doe'

    def test_user_str(self):
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPass123!'
        )
        assert str(user) == 'test@example.com'

    def test_loyalty_points(self):
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPass123!'
        )
        user.add_loyalty_points(100)
        assert user.loyalty_points == 100
        assert user.deduct_loyalty_points(50) is True
        assert user.loyalty_points == 50

    def test_deduct_insufficient_points(self):
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPass123!'
        )
        assert user.deduct_loyalty_points(100) is False
        assert user.loyalty_points == 0


@pytest.mark.django_db
class TestProductModel:
    def test_product_creation(self, product):
        assert product.name == 'Test Product'
        assert product.price == Decimal('29.99')
        assert product.is_in_stock is True

    def test_product_is_on_sale(self, product):
        product.compare_at_price = Decimal('39.99')
        product.save()
        assert product.is_on_sale is True
        assert product.discount_percentage == 25

    def test_product_not_on_sale(self, product):
        assert product.is_on_sale is False
        assert product.discount_percentage == 0

    def test_product_slug_generation(self, category):
        from apps.products.models import Product
        p = Product.objects.create(
            name='New Product',
            slug='new-product',
            sku='NP001',
            category=category,
            price=Decimal('19.99'),
            status='active',
        )
        assert p.slug == 'new-product'


@pytest.mark.django_db
class TestCategoryModel:
    def test_category_creation(self, category):
        assert category.name == 'Electronics'
        assert category.slug == 'electronics'

    def test_category_str(self, category):
        assert str(category) == 'Electronics'


@pytest.mark.django_db
class TestCartModel:
    def test_cart_creation(self, cart, user):
        assert cart.user == user
        assert cart.is_active is True
        assert cart.subtotal == Decimal('0.00')

    def test_cart_add_item(self, cart, product):
        item = cart.add_item(product, quantity=2)
        assert item.quantity == 2
        assert cart.total_items == 2

    def test_cart_total(self, cart, product):
        cart.add_item(product, quantity=2)
        assert cart.subtotal == Decimal('59.98')


@pytest.mark.django_db
class TestOrderModel:
    def test_order_number_generation(self):
        from apps.orders.models import Order
        order = Order.objects.create(
            shipping_first_name='John',
            shipping_last_name='Doe',
            shipping_address_line1='123 Main St',
            shipping_city='New York',
            shipping_state='NY',
            shipping_postal_code='10001',
            shipping_country='US',
        )
        assert order.order_number is not None
        assert order.order_number.startswith('ORD-')

    def test_order_status_transitions(self):
        from apps.orders.models import Order
        order = Order.objects.create(
            shipping_first_name='John',
            shipping_last_name='Doe',
            shipping_address_line1='123 Main St',
            shipping_city='New York',
            shipping_state='NY',
            shipping_postal_code='10001',
            shipping_country='US',
        )
        order.confirm()
        assert order.status == 'confirmed'
        order.ship()
        assert order.status == 'shipped'
        order.deliver()
        assert order.status == 'delivered'


@pytest.mark.django_db
class TestCouponModel:
    def test_coupon_validity(self):
        from apps.marketing.models import Coupon
        from django.utils import timezone
        from datetime import timedelta
        coupon = Coupon.objects.create(
            code='TEST10',
            discount_type='percentage',
            discount_value=Decimal('10'),
            start_date=timezone.now() - timedelta(days=1),
            end_date=timezone.now() + timedelta(days=30),
            is_active=True,
        )
        assert coupon.is_valid is True

    def test_coupon_discount_calculation(self):
        from apps.marketing.models import Coupon
        from django.utils import timezone
        from datetime import timedelta
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
        from django.utils import timezone
        from datetime import timedelta
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
