from django.db import models
from apps.common.models import TimeStampedModel, UUIDModel


class Report(UUIDModel, TimeStampedModel):
    REPORT_TYPES = [
        ('sales', 'Sales Report'),
        ('inventory', 'Inventory Report'),
        ('customers', 'Customer Report'),
        ('products', 'Product Report'),
        ('orders', 'Order Report'),
        ('financial', 'Financial Report'),
        ('marketing', 'Marketing Report'),
        ('custom', 'Custom Report'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('generating', 'Generating'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    date_from = models.DateField(null=True, blank=True)
    date_to = models.DateField(null=True, blank=True)
    filters = models.JSONField(default=dict, blank=True)
    data = models.JSONField(default=dict, blank=True)
    file = models.FileField(upload_to='reports/%Y/%m/', blank=True, null=True)
    generated_by = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL,
        null=True, blank=True
    )
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True, default='')

    class Meta:
        verbose_name = 'Report'
        verbose_name_plural = 'Reports'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_report_type_display()})"


class AnalyticsEvent(UUIDModel, TimeStampedModel):
    EVENT_TYPES = [
        ('page_view', 'Page View'),
        ('product_view', 'Product View'),
        ('add_to_cart', 'Add to Cart'),
        ('remove_from_cart', 'Remove from Cart'),
        ('begin_checkout', 'Begin Checkout'),
        ('purchase', 'Purchase'),
        ('search', 'Search'),
        ('promotion_click', 'Promotion Click'),
        ('email_open', 'Email Open'),
        ('email_click', 'Email Click'),
    ]
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES, db_index=True)
    user = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='analytics_events'
    )
    session_key = models.CharField(max_length=255, blank=True, default='')
    page_url = models.URLField(blank=True, default='')
    product = models.ForeignKey(
        'products.Product', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='analytics_events'
    )
    order = models.ForeignKey(
        'orders.Order', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='analytics_events'
    )
    data = models.JSONField(default=dict, blank=True)
    revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, default='')
    referrer = models.URLField(blank=True, default='')

    class Meta:
        verbose_name = 'Analytics Event'
        verbose_name_plural = 'Analytics Events'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['event_type', 'created_at']),
            models.Index(fields=['user', 'event_type']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.event_type} - {self.created_at}"


class DailyStats(UUIDModel):
    date = models.DateField(unique=True, db_index=True)
    total_orders = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_items_sold = models.PositiveIntegerField(default=0)
    average_order_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    new_customers = models.PositiveIntegerField(default=0)
    returning_customers = models.PositiveIntegerField(default=0)
    page_views = models.PositiveIntegerField(default=0)
    unique_visitors = models.PositiveIntegerField(default=0)
    conversion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    refund_count = models.PositiveIntegerField(default=0)
    refund_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'Daily Stats'
        verbose_name_plural = 'Daily Stats'
        ordering = ['-date']

    def __str__(self):
        return f"Stats for {self.date}"


class ProductPerformance(UUIDModel):
    product = models.ForeignKey(
        'products.Product', on_delete=models.CASCADE,
        related_name='performance_data'
    )
    date = models.DateField(db_index=True)
    views = models.PositiveIntegerField(default=0)
    add_to_carts = models.PositiveIntegerField(default=0)
    purchases = models.PositiveIntegerField(default=0)
    revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    conversion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'Product Performance'
        verbose_name_plural = 'Product Performance'
        unique_together = ['product', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.product.name} - {self.date}"


class SalesForecast(UUIDModel):
    date = models.DateField(db_index=True)
    predicted_revenue = models.DecimalField(max_digits=12, decimal_places=2)
    predicted_orders = models.PositiveIntegerField()
    confidence = models.DecimalField(max_digits=5, decimal_places=2)
    actual_revenue = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    actual_orders = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        verbose_name = 'Sales Forecast'
        verbose_name_plural = 'Sales Forecasts'
        ordering = ['date']

    def __str__(self):
        return f"Forecast for {self.date}"
