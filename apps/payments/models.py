from django.db import models
from django.conf import settings
from decimal import Decimal
from apps.common.models import TimeStampedModel, UUIDModel


class PaymentGateway(UUIDModel, TimeStampedModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    config = models.JSONField(default=dict, blank=True)
    supported_currencies = models.JSONField(default=list, blank=True)
    fee_percent = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('2.90'))
    fee_fixed = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.30'))
    test_mode = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Payment Gateway'
        verbose_name_plural = 'Payment Gateways'

    def __str__(self):
        return f"{self.name} ({'Test' if self.test_mode else 'Live'})"

    def calculate_fee(self, amount):
        percentage_fee = amount * (self.fee_percent / Decimal('100'))
        return percentage_fee + self.fee_fixed


class Transaction(UUIDModel, TimeStampedModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
        ('partially_refunded', 'Partially Refunded'),
        ('disputed', 'Disputed'),
    ]
    TYPE_CHOICES = [
        ('payment', 'Payment'),
        ('refund', 'Refund'),
        ('chargeback', 'Chargeback'),
        ('capture', 'Capture'),
        ('void', 'Void'),
        ('authorization', 'Authorization'),
    ]
    gateway = models.ForeignKey(PaymentGateway, on_delete=models.PROTECT, related_name='transactions')
    order = models.ForeignKey(
        'orders.Order', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='transactions'
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    transaction_id = models.CharField(max_length=200, unique=True, db_index=True)
    reference_id = models.CharField(max_length=200, blank=True, default='')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='payment')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    fee = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    net_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=6, default=Decimal('1.000000'))
    payment_method = models.CharField(max_length=50, blank=True, default='')
    card_last_four = models.CharField(max_length=4, blank=True, default='')
    card_brand = models.CharField(max_length=20, blank=True, default='')
    gateway_response = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True, default='')
    metadata = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['transaction_id']),
            models.Index(fields=['order', 'status']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['gateway', 'status']),
        ]

    def __str__(self):
        return f"Transaction {self.transaction_id} - ${self.amount} ({self.status})"

    def complete(self):
        from django.utils import timezone
        self.status = 'completed'
        self.processed_at = timezone.now()
        self.save(update_fields=['status', 'processed_at', 'updated_at'])

    def fail(self, error_message=''):
        self.status = 'failed'
        self.error_message = error_message
        self.save(update_fields=['status', 'error_message', 'updated_at'])

    @property
    def is_successful(self):
        return self.status == 'completed'


class Refund(UUIDModel, TimeStampedModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='refunds')
    order = models.ForeignKey(
        'orders.Order', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='refunds'
    )
    refund_id = models.CharField(max_length=200, unique=True, db_index=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    gateway_response = models.JSONField(default=dict, blank=True)
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Refund'
        verbose_name_plural = 'Refunds'
        ordering = ['-created_at']

    def __str__(self):
        return f"Refund {self.refund_id} - ${self.amount}"

    def save(self, *args, **kwargs):
        if not self.refund_id:
            from apps.common.utils import generate_refund_number
            self.refund_id = generate_refund_number()
        super().save(*args, **kwargs)

    def complete(self, processed_by=None):
        from django.utils import timezone
        self.status = 'completed'
        self.processed_by = processed_by
        self.processed_at = timezone.now()
        self.save(update_fields=['status', 'processed_by', 'processed_at', 'updated_at'])
        self.transaction.status = 'refunded'
        self.transaction.save(update_fields=['status', 'updated_at'])


class PaymentMethod(UUIDModel, TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_payment_methods')
    gateway = models.ForeignKey(PaymentGateway, on_delete=models.CASCADE)
    token = models.CharField(max_length=500)
    payment_type = models.CharField(max_length=50)
    last_four = models.CharField(max_length=4, blank=True, default='')
    card_brand = models.CharField(max_length=20, blank=True, default='')
    expiry_month = models.PositiveIntegerField(null=True, blank=True)
    expiry_year = models.PositiveIntegerField(null=True, blank=True)
    is_default = models.BooleanField(default=False)
    billing_address = models.ForeignKey(
        'users.Address', on_delete=models.SET_NULL,
        null=True, blank=True
    )

    class Meta:
        verbose_name = 'Payment Method'
        verbose_name_plural = 'Payment Methods'
        ordering = ['-is_default']

    def __str__(self):
        return f"{self.card_brand} ****{self.last_four}"

    def save(self, *args, **kwargs):
        if self.is_default:
            PaymentMethod.objects.filter(
                user=self.user, is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        from django.utils import timezone
        now = timezone.now()
        if self.expiry_year and self.expiry_month:
            return now.year > self.expiry_year or (
                now.year == self.expiry_year and now.month > self.expiry_month
            )
        return False


class WebhookEvent(UUIDModel, TimeStampedModel):
    gateway = models.ForeignKey(PaymentGateway, on_delete=models.CASCADE, related_name='webhook_events')
    event_id = models.CharField(max_length=200, unique=True)
    event_type = models.CharField(max_length=100)
    payload = models.JSONField()
    processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True, default='')

    class Meta:
        verbose_name = 'Webhook Event'
        verbose_name_plural = 'Webhook Events'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.event_type} - {self.event_id}"

    def mark_processed(self):
        from django.utils import timezone
        self.processed = True
        self.processed_at = timezone.now()
        self.save(update_fields=['processed', 'processed_at', 'updated_at'])


class PaymentLog(UUIDModel, TimeStampedModel):
    transaction = models.ForeignKey(
        Transaction, on_delete=models.CASCADE,
        null=True, blank=True, related_name='logs'
    )
    gateway_code = models.CharField(max_length=50)
    action = models.CharField(max_length=100)
    request_data = models.JSONField(default=dict, blank=True)
    response_data = models.JSONField(default=dict, blank=True)
    status_code = models.IntegerField(null=True, blank=True)
    duration_ms = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name = 'Payment Log'
        verbose_name_plural = 'Payment Logs'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.gateway_code} - {self.action}"
