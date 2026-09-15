import factory
from apps.cart.models import Cart


class CartFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Cart
