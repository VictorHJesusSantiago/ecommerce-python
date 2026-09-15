import factory
from apps.orders.models import Order


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order
    status = 'pending'
