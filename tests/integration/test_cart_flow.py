import pytest
from rest_framework import status


@pytest.mark.django_db
class TestCartFlow:
    def test_cart_operations(self, authenticated_client, product):
        add_response = authenticated_client.post('/api/v1/cart/add-item/', {
            'product_id': str(product.id),
            'quantity': 3,
        })
        assert add_response.status_code == status.HTTP_201_CREATED

        cart_response = authenticated_client.get('/api/v1/cart/')
        assert cart_response.data['cart']['total_items'] == 3

        items = cart_response.data['cart']['items']
        update_response = authenticated_client.post('/api/v1/cart/update-item/', {
            'item_id': items[0]['id'],
            'quantity': 5,
        }, format='json')
        assert update_response.status_code == status.HTTP_200_OK

        summary_response = authenticated_client.get('/api/v1/cart/summary/')
        assert summary_response.status_code == status.HTTP_200_OK
        assert summary_response.data['total_items'] == 5

        clear_response = authenticated_client.post('/api/v1/cart/clear/')
        assert clear_response.status_code == status.HTTP_200_OK

        cart_response = authenticated_client.get('/api/v1/cart/')
        assert cart_response.data['cart']['total_items_count'] == 0
