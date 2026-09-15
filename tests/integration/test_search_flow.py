import pytest
from rest_framework import status


@pytest.mark.django_db
class TestSearchFlow:
    def test_search_products(self, api_client, product):
        response = api_client.get('/api/v1/search/?q=Test')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True

    def test_autocomplete(self, api_client, product):
        response = api_client.get('/api/v1/autocomplete/?q=Te')
        assert response.status_code == status.HTTP_200_OK
