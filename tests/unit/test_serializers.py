import pytest
from decimal import Decimal
from apps.users.serializers import UserRegistrationSerializer, UserSerializer
from apps.products.serializers import ProductListSerializer, CategorySerializer


@pytest.mark.django_db
class TestUserRegistrationSerializer:
    def test_valid_registration(self):
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'StrongPass123!',
            'password_confirm': 'StrongPass123!',
        }
        serializer = UserRegistrationSerializer(data=data)
        assert serializer.is_valid()

    def test_password_mismatch(self):
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'Pass123!',
            'password_confirm': 'DifferentPass123!',
        }
        serializer = UserRegistrationSerializer(data=data)
        assert not serializer.is_valid()
        assert 'password_confirm' in serializer.errors


@pytest.mark.django_db
class TestUserSerializer:
    def test_user_serialization(self, user):
        serializer = UserSerializer(user)
        data = serializer.data
        assert data['email'] == 'test@example.com'
        assert 'full_name' in data


@pytest.mark.django_db
class TestProductSerializer:
    def test_product_list_serialization(self, product):
        serializer = ProductListSerializer(product)
        data = serializer.data
        assert data['name'] == 'Test Product'
        assert data['price'] == '29.99'


@pytest.mark.django_db
class TestCategorySerializer:
    def test_category_serialization(self, category):
        serializer = CategorySerializer(category)
        data = serializer.data
        assert data['name'] == 'Electronics'
