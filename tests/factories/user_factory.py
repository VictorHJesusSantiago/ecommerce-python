import factory
from apps.users.models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    email = factory.Faker('email')
    username = factory.Faker('user_name')
