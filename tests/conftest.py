import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email='test@example.com',
        username='testuser',
        password='TestPass123!',
        first_name='Test',
        last_name='User',
    )


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        email='admin@example.com',
        username='admin',
        password='AdminPass123!',
    )


@pytest.fixture
def vendor_user(db):
    user = User.objects.create_user(
        email='vendor@example.com',
        username='vendor',
        password='VendorPass123!',
        role='vendor',
    )
    from apps.users.models import VendorProfile
    VendorProfile.objects.create(user=user, shop_name='Test Shop')
    return user


@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def category(db):
    from apps.products.models import Category
    return Category.objects.create(name='Electronics', slug='electronics')


@pytest.fixture
def product(db, category):
    from apps.products.models import Product
    return Product.objects.create(
        name='Test Product',
        slug='test-product',
        sku='TEST001',
        category=category,
        price=29.99,
        quantity=100,
        status='active',
        is_active=True,
    )


@pytest.fixture
def cart(db, user):
    from apps.cart.models import Cart
    return Cart.objects.create(user=user, is_active=True)
