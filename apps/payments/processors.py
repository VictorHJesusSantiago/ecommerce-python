import json
import hashlib
import hmac
import logging
from decimal import Decimal

logger = logging.getLogger('apps.payments')


class BasePaymentProcessor:
    def process_payment(self, amount, currency='USD', **kwargs):
        raise NotImplementedError

    def process_refund(self, transaction_id, amount, **kwargs):
        raise NotImplementedError

    def verify_webhook(self, payload, signature):
        raise NotImplementedError

    def process_event(self, event_data):
        raise NotImplementedError


class StripeProcessor(BasePaymentProcessor):
    def __init__(self):
        from django.conf import settings
        import stripe
        stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')
        self.stripe = stripe

    def process_payment(self, amount, currency='USD', token=None, **kwargs):
        try:
            charge = self.stripe.Charge.create(
                amount=int(amount * 100),
                currency=currency.lower(),
                source=token,
                description=kwargs.get('description', ''),
                metadata=kwargs.get('metadata', {}),
            )
            return {
                'success': True,
                'transaction_id': charge.id,
                'status': charge.status,
                'amount': Decimal(charge.amount) / 100,
            }
        except self.stripe.error.CardError as e:
            return {'success': False, 'error': str(e)}
        except Exception as e:
            logger.exception(f"Stripe payment error: {e}")
            return {'success': False, 'error': 'Payment processing failed.'}

    def process_refund(self, transaction_id, amount=None, **kwargs):
        try:
            refund = self.stripe.Refund.create(
                charge=transaction_id,
                amount=int(amount * 100) if amount else None,
            )
            return {
                'success': True,
                'refund_id': refund.id,
                'status': refund.status,
            }
        except Exception as e:
            logger.exception(f"Stripe refund error: {e}")
            return {'success': False, 'error': str(e)}

    def verify_webhook(self, payload, sig_header):
        from django.conf import settings
        webhook_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', '')
        try:
            event = self.stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
            return event
        except Exception as e:
            logger.exception(f"Stripe webhook verification failed: {e}")
            return None

    def process_event(self, event_data):
        event_type = event_data.get('type', '')
        data = event_data.get('data', {}).get('object', {})

        if event_type == 'payment_intent.succeeded':
            self._handle_payment_success(data)
        elif event_type == 'payment_intent.payment_failed':
            self._handle_payment_failure(data)
        elif event_type == 'charge.refunded':
            self._handle_refund(data)

    def _handle_payment_success(self, data):
        from .models import Transaction
        transaction_id = data.get('id')
        try:
            transaction = Transaction.objects.get(transaction_id=transaction_id)
            transaction.complete()
        except Transaction.DoesNotExist:
            pass

    def _handle_payment_failure(self, data):
        from .models import Transaction
        transaction_id = data.get('id')
        try:
            transaction = Transaction.objects.get(transaction_id=transaction_id)
            transaction.fail(error_message=data.get('last_payment_error', {}).get('message', 'Payment failed'))
        except Transaction.DoesNotExist:
            pass

    def _handle_refund(self, data):
        from .models import Refund
        refund_id = data.get('id')
        try:
            refund = Refund.objects.get(refund_id=refund_id)
            refund.complete()
        except Refund.DoesNotExist:
            pass


class PayPalProcessor(BasePaymentProcessor):
    def __init__(self):
        from django.conf import settings
        self.client_id = getattr(settings, 'PAYPAL_CLIENT_ID', '')
        self.client_secret = getattr(settings, 'PAYPAL_CLIENT_SECRET', '')

    def process_payment(self, amount, currency='USD', **kwargs):
        try:
            import paypalrestsdk
            payment = paypalrestsdk.Payment({
                'intent': 'sale',
                'payer': {'payment_method': 'paypal'},
                'transactions': [{
                    'amount': {'total': str(amount), 'currency': currency},
                    'description': kwargs.get('description', ''),
                }],
                'redirect_urls': {
                    'return_url': kwargs.get('return_url', ''),
                    'cancel_url': kwargs.get('cancel_url', ''),
                }
            })
            if payment.create():
                return {
                    'success': True,
                    'transaction_id': payment.id,
                    'status': 'pending',
                    'approval_url': next(
                        link.href for link in payment.links if link.rel == 'approval_url'
                    ),
                }
            return {'success': False, 'error': payment.error.get('message', 'Payment failed')}
        except Exception as e:
            logger.exception(f"PayPal payment error: {e}")
            return {'success': False, 'error': 'Payment processing failed.'}

    def process_refund(self, transaction_id, amount, **kwargs):
        try:
            import paypalrestsdk
            sale = paypalrestsdk.Sale.find(transaction_id)
            refund = sale.refund({'amount': {'total': str(amount), 'currency': 'USD'}})
            if refund.success():
                return {'success': True, 'refund_id': refund.id}
            return {'success': False, 'error': refund.error.get('message', 'Refund failed')}
        except Exception as e:
            logger.exception(f"PayPal refund error: {e}")
            return {'success': False, 'error': str(e)}

    def verify_webhook(self, payload, signature):
        return payload

    def process_event(self, event_data):
        event_type = event_data.get('event_type', '')
        if event_type == 'PAYMENT.SALE.COMPLETED':
            pass


class MockProcessor(BasePaymentProcessor):
    def process_payment(self, amount, currency='USD', **kwargs):
        return {
            'success': True,
            'transaction_id': f'mock_{hash(str(amount))}',
            'status': 'completed',
            'amount': amount,
        }

    def process_refund(self, transaction_id, amount, **kwargs):
        return {
            'success': True,
            'refund_id': f'mock_refund_{hash(str(amount))}',
            'status': 'completed',
        }

    def verify_webhook(self, payload, signature):
        return True

    def process_event(self, event_data):
        pass


def get_processor(gateway_code):
    processors = {
        'stripe': StripeProcessor,
        'paypal': PayPalProcessor,
        'mock': MockProcessor,
    }
    processor_class = processors.get(gateway_code, MockProcessor)
    return processor_class()
