import pytest
from rest_framework import status


@pytest.mark.django_db
class TestUserRegistration:
    def test_register_success(self, api_client):
        data = {
            'email': 'new@example.com',
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'StrongPass123!',
            'password_confirm': 'StrongPass123!',
        }
        response = api_client.post('/api/v1/users/register/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['success'] is True

    def test_register_password_mismatch(self, api_client):
        data = {
            'email': 'new@example.com',
            'username': 'newuser',
            'password': 'Pass123!',
            'password_confirm': 'DifferentPass123!',
        }
        response = api_client.post('/api/v1/users/register/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_duplicate_email(self, api_client, user):
        data = {
            'email': 'test@example.com',
            'username': 'another',
            'password': 'Pass123!',
            'password_confirm': 'Pass123!',
        }
        response = api_client.post('/api/v1/users/register/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUserLogin:
    def test_login_success(self, api_client, user):
        data = {
            'email': 'test@example.com',
            'password': 'TestPass123!',
        }
        response = api_client.post('/api/v1/users/login/', data)
        assert response.status_code == status.HTTP_200_OK
        assert 'tokens' in response.data

    def test_login_invalid_credentials(self, api_client):
        data = {
            'email': 'wrong@example.com',
            'password': 'wrongpass',
        }
        response = api_client.post('/api/v1/users/login/', data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestUserProfile:
    def test_get_profile(self, authenticated_client):
        response = authenticated_client.get('/api/v1/users/profile/')
        assert response.status_code == status.HTTP_200_OK

    def test_update_profile(self, authenticated_client):
        data = {'first_name': 'Updated', 'last_name': 'Name'}
        response = authenticated_client.patch('/api/v1/users/profile/update/', data)
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestProductAPI:
    def test_list_products(self, api_client, product):
        response = api_client.get('/api/v1/products/')
        assert response.status_code == status.HTTP_200_OK

    def test_get_product(self, api_client, product):
        response = api_client.get(f'/api/v1/products/{product.id}/')
        assert response.status_code == status.HTTP_200_OK

    def test_search_products(self, api_client, product):
        response = api_client.get('/api/v1/products/?search=Test')
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestCategoryAPI:
    def test_list_categories(self, api_client, category):
        response = api_client.get('/api/v1/categories/')
        assert response.status_code == status.HTTP_200_OK

    def test_get_category(self, api_client, category):
        response = api_client.get(f'/api/v1/categories/{category.id}/')
        assert response.status_code == status.HTTP_200_OK

    def test_category_tree(self, api_client, category):
        response = api_client.get('/api/v1/categories/tree/')
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestCartAPI:
    def test_get_cart(self, authenticated_client):
        response = authenticated_client.get('/api/v1/cart/')
        assert response.status_code == status.HTTP_200_OK

    def test_add_to_cart(self, authenticated_client, product):
        data = {
            'product_id': str(product.id),
            'quantity': 1,
        }
        response = authenticated_client.post('/api/v1/cart/add-item/', data)
        assert response.status_code == status.HTTP_201_CREATED

    def test_clear_cart(self, authenticated_client, cart):
        response = authenticated_client.post('/api/v1/cart/clear/')
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestReviewAPI:
    def test_list_reviews(self, api_client, product):
        response = api_client.get('/api/v1/reviews/')
        assert response.status_code == status.HTTP_200_OK

    def test_create_review(self, authenticated_client, product):
        data = {
            'product_id': str(product.id),
            'rating': 5,
            'body': 'Great product! I love it.',
        }
        response = authenticated_client.post('/api/v1/reviews/', data)
        assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
class TestOrderAPI:
    def test_list_orders(self, authenticated_client):
        response = authenticated_client.get('/api/v1/orders/')
        assert response.status_code == status.HTTP_200_OK
