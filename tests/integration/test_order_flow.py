import pytest
from decimal import Decimal
from rest_framework import status


@pytest.mark.django_db
class TestOrderFlow:
    def test_complete_order_flow(self, authenticated_client, product):
        add_response = authenticated_client.post('/api/v1/cart/add-item/', {
            'product_id': str(product.id),
            'quantity': 2,
        })
        assert add_response.status_code == status.HTTP_201_CREATED

        cart_response = authenticated_client.get('/api/v1/cart/')
        assert cart_response.status_code == status.HTTP_200_OK
        assert cart_response.data['cart']['total_items'] == 2

        from apps.users.models import Address
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.get(email='test@example.com')
        address = Address.objects.create(
            user=user,
            first_name='John',
            last_name='Doe',
            address_line1='123 Main St',
            city='New York',
            state='NY',
            postal_code='10001',
            country='US',
            is_default=True,
        )

        order_response = authenticated_client.post('/api/v1/orders/', {
            'shipping_address_id': str(address.id),
            'payment_method': 'credit_card',
        }, format='json')
        assert order_response.status_code == status.HTTP_201_CREATED
        assert order_response.data['success'] is True

        order_number = order_response.data['order']['order_number']
        detail_response = authenticated_client.get(f'/api/v1/orders/{order_number}/')
        assert detail_response.status_code == status.HTTP_200_OK

        cart_response = authenticated_client.get('/api/v1/cart/')
        assert cart_response.data['cart']['total_items_count'] == 0
