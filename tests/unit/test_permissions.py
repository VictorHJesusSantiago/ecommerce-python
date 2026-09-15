import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory
from apps.common.permissions import IsOwner, IsAdminUser, IsCustomer, ReadOnly

User = get_user_model()


@pytest.mark.django_db
class TestPermissions:
    def test_is_admin_permission(self):
        permission = IsAdminUser()
        factory = APIRequestFactory()
        request = factory.get('/test/')

        request.user = User.objects.create_superuser(email='admin@test.com', password='pass')
        assert permission.has_permission(request, None) is True

        request.user = User.objects.create_user(email='user@test.com', password='pass')
        assert permission.has_permission(request, None) is False

    def test_is_customer_permission(self):
        permission = IsCustomer()
        factory = APIRequestFactory()
        request = factory.get('/test/')

        request.user = User.objects.create_user(email='user@test.com', password='pass', role='customer')
        assert permission.has_permission(request, None) is True

        request.user = User.objects.create_superuser(email='admin@test.com', password='pass')
        assert permission.has_permission(request, None) is False

    def test_read_only_permission(self):
        permission = ReadOnly()
        factory = APIRequestFactory()

        request = factory.get('/test/')
        assert permission.has_permission(request, None) is True

        request = factory.post('/test/')
        assert permission.has_permission(request, None) is False
