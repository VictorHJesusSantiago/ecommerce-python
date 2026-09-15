import pytest
from decimal import Decimal
from apps.payments.models import Transaction, Refund, PaymentGateway


@pytest.mark.django_db
class TestPaymentGateway:
    def test_gateway_creation(self):
        gateway = PaymentGateway.objects.create(
            name='Stripe',
            code='stripe',
            fee_percent=Decimal('2.90'),
            fee_fixed=Decimal('0.30'),
        )
        assert gateway.name == 'Stripe'

    def test_calculate_fee(self):
        gateway = PaymentGateway.objects.create(
            name='Stripe',
            code='stripe',
            fee_percent=Decimal('2.90'),
            fee_fixed=Decimal('0.30'),
        )
        fee = gateway.calculate_fee(Decimal('100'))
        assert fee == Decimal('3.20')


@pytest.mark.django_db
class TestTransaction:
    def test_transaction_creation(self):
        gateway = PaymentGateway.objects.create(name='Stripe', code='stripe')
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(email='test@test.com', password='pass')
        transaction = Transaction.objects.create(
            gateway=gateway,
            user=user,
            transaction_id='TXN123456',
            amount=Decimal('100.00'),
        )
        assert transaction.status == 'pending'

    def test_transaction_completion(self):
        gateway = PaymentGateway.objects.create(name='Stripe', code='stripe')
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(email='test@test.com', password='pass')
        transaction = Transaction.objects.create(
            gateway=gateway,
            user=user,
            transaction_id='TXN123456',
            amount=Decimal('100.00'),
        )
        transaction.complete()
        assert transaction.status == 'completed'
        assert transaction.processed_at is not None
