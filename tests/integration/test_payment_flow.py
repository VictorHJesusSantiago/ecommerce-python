import pytest
from rest_framework import status


@pytest.mark.django_db
class TestPaymentFlow:
    def test_payment_processing(self, authenticated_client, product):
        from apps.users.models import Address
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.get(email='test@example.com')

        authenticated_client.post('/api/v1/cart/add-item/', {
            'product_id': str(product.id),
            'quantity': 1,
        })

        address = Address.objects.create(
            user=user, first_name='John', last_name='Doe',
            address_line1='123 Main St', city='New York',
            state='NY', postal_code='10001', country='US', is_default=True,
        )

        order_response = authenticated_client.post('/api/v1/orders/', {
            'shipping_address_id': str(address.id),
            'payment_method': 'credit_card',
        }, format='json')
        assert order_response.status_code == status.HTTP_201_CREATED
