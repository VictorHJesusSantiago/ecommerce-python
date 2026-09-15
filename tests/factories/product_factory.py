import factory
from apps.products.models import Product


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product
    name = factory.Faker('sentence', nb_words=3)
    slug = factory.Faker('slug')
    price = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True)
