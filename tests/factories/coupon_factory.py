import factory
from apps.marketing.models import Coupon


class CouponFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Coupon
    code = factory.Faker('bothify', text='####-????')
    discount_value = 10
