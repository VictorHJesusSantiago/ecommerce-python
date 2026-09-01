from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
from apps.common.models import TimeStampedModel, UUIDModel, ActivatableModel, SEOModel


class Coupon(UUIDModel, TimeStampedModel, ActivatableModel):
    DISCOUNT_TYPES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
        ('free_shipping', 'Free Shipping'),
        ('buy_x_get_y', 'Buy X Get Y'),
    ]
    code = models.CharField(max_length=50, unique=True, db_index=True)
    description = models.TextField(blank=True, default='')
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES, default='percentage')
    discount_value = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    max_discount_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    min_order_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    max_uses = models.PositiveIntegerField(null=True, blank=True)
    max_uses_per_user = models.PositiveIntegerField(default=1)
    times_used = models.PositiveIntegerField(default=0)
    applicable_products = models.ManyToManyField(
        'products.Product', blank=True, related_name='coupons'
    )
    applicable_categories = models.ManyToManyField(
        'products.Category', blank=True, related_name='coupons'
    )
    exclude_products = models.ManyToManyField(
        'products.Product', blank=True, related_name='excluded_coupons'
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_combinable = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True
    )

    class Meta:
        verbose_name = 'Coupon'
        verbose_name_plural = 'Coupons'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code} ({self.get_discount_type_display()})"

    @property
    def is_valid(self):
        now = timezone.now()
        return (
            self.is_active and
            self.start_date <= now <= self.end_date and
            (self.max_uses is None or self.times_used < self.max_uses)
        )

    def is_valid_for_user(self, user):
        if not self.is_valid:
            return False
        if self.max_uses_per_user:
            usage = CouponUsage.objects.filter(
                coupon=self, user=user
            ).count()
            if usage >= self.max_uses_per_user:
                return False
        return True

    def calculate_discount(self, subtotal):
        if not self.is_valid:
            return Decimal('0.00')
        if self.discount_type == 'percentage':
            discount = subtotal * (self.discount_value / Decimal('100'))
            if self.max_discount_amount:
                discount = min(discount, self.max_discount_amount)
            return discount
        elif self.discount_type == 'fixed':
            return min(self.discount_value, subtotal)
        return Decimal('0.00')

    def use(self, user=None, order=None):
        self.times_used += 1
        self.save(update_fields=['times_used', 'updated_at'])
        if user:
            CouponUsage.objects.create(
                coupon=self, user=user, order=order,
                discount_amount=self.calculate_discount(
                    order.subtotal if order else Decimal('0.00')
                )
            )


class CouponUsage(UUIDModel, TimeStampedModel):
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='usages')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='coupon_usages')
    order = models.ForeignKey(
        'orders.Order', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='coupon_usages'
    )
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    class Meta:
        verbose_name = 'Coupon Usage'
        verbose_name_plural = 'Coupon Usages'
        unique_together = ['coupon', 'user', 'order']

    def __str__(self):
        return f"{self.user.email} used {self.coupon.code}"


class Promotion(UUIDModel, TimeStampedModel, ActivatableModel):
    PROMOTION_TYPES = [
        ('sale', 'Sale'),
        ('bundle', 'Bundle'),
        ('flash_sale', 'Flash Sale'),
        ('clearance', 'Clearance'),
        ('loyalty', 'Loyalty Reward'),
    ]
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True, default='')
    promotion_type = models.CharField(max_length=20, choices=PROMOTION_TYPES, default='sale')
    discount_type = models.CharField(
        max_length=20,
        choices=[('percentage', 'Percentage'), ('fixed', 'Fixed Amount')],
        default='percentage'
    )
    discount_value = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    products = models.ManyToManyField('products.Product', blank=True, related_name='promotions')
    banner_image = models.ImageField(upload_to='promotions/', blank=True, null=True)
    priority = models.IntegerField(default=0)
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    times_used = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Promotion'
        verbose_name_plural = 'Promotions'
        ordering = ['-priority', '-start_date']

    def __str__(self):
        return self.name

    @property
    def is_active_promotion(self):
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date

    @property
    def products_count(self):
        return self.products.filter(is_active=True).count()


class Banner(UUIDModel, TimeStampedModel, ActivatableModel):
    TITLE_CHOICES = [
        ('hero', 'Hero Banner'),
        ('promo', 'Promotion'),
        ('seasonal', 'Seasonal'),
        ('category', 'Category'),
    ]
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True, default='')
    image = models.ImageField(upload_to='banners/%Y/%m/')
    mobile_image = models.ImageField(upload_to='banners/%Y/%m/', blank=True, null=True)
    link_url = models.URLField(blank=True, default='')
    banner_type = models.CharField(max_length=20, choices=TITLE_CHOICES, default='hero')
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    sort_order = models.IntegerField(default=0)
    impressions = models.PositiveIntegerField(default=0)
    clicks = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Banner'
        verbose_name_plural = 'Banners'
        ordering = ['sort_order', '-created_at']

    def __str__(self):
        return self.title

    @property
    def is_active_banner(self):
        now = timezone.now()
        if not self.is_active:
            return False
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        return True

    @property
    def click_through_rate(self):
        if self.impressions > 0:
            return round((self.clicks / self.impressions) * 100, 2)
        return 0

    def record_impression(self):
        self.impressions += 1
        self.save(update_fields=['impressions'])

    def record_click(self):
        self.clicks += 1
        self.save(update_fields=['clicks'])


class Newsletter(UUIDModel, TimeStampedModel):
    email = models.EmailField(unique=True, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='newsletter_subscriptions'
    )
    is_active = models.BooleanField(default=True)
    confirmed = models.BooleanField(default=False)
    confirmation_token = models.CharField(max_length=100, blank=True, default='')
    source = models.CharField(max_length=50, default='website')
    tags = models.JSONField(default=list, blank=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Newsletter Subscription'
        verbose_name_plural = 'Newsletter Subscriptions'
        ordering = ['-subscribed_at']

    def __str__(self):
        return self.email

    def unsubscribe(self):
        self.is_active = False
        self.unsubscribed_at = timezone.now()
        self.save(update_fields=['is_active', 'unsubscribed_at', 'updated_at'])


class EmailCampaign(UUIDModel, TimeStampedModel):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('sending', 'Sending'),
        ('sent', 'Sent'),
        ('cancelled', 'Cancelled'),
    ]
    name = models.CharField(max_length=200)
    subject = models.CharField(max_length=200)
    preview_text = models.CharField(max_length=200, blank=True, default='')
    html_content = models.TextField(blank=True, default='')
    plain_text_content = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    total_recipients = models.PositiveIntegerField(default=0)
    total_sent = models.PositiveIntegerField(default=0)
    total_opened = models.PositiveIntegerField(default=0)
    total_clicked = models.PositiveIntegerField(default=0)
    total_bounced = models.PositiveIntegerField(default=0)
    total_unsubscribed = models.PositiveIntegerField(default=0)
    segment = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = 'Email Campaign'
        verbose_name_plural = 'Email Campaigns'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def open_rate(self):
        if self.total_sent > 0:
            return round((self.total_opened / self.total_sent) * 100, 2)
        return 0

    @property
    def click_rate(self):
        if self.total_sent > 0:
            return round((self.total_clicked / self.total_sent) * 100, 2)
        return 0


class LoyaltyProgram(UUIDModel, TimeStampedModel, ActivatableModel):
    name = models.CharField(max_length=200)
    points_per_dollar = models.PositiveIntegerField(default=1)
    redemption_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.01'))
    min_points_redeem = models.PositiveIntegerField(default=100)
    tier_thresholds = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = 'Loyalty Program'
        verbose_name_plural = 'Loyalty Programs'

    def __str__(self):
        return self.name


class ReferralProgram(UUIDModel, TimeStampedModel, ActivatableModel):
    referrer_reward = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('10.00'))
    referee_reward = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('10.00'))
    min_purchase_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    max_referrals = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        verbose_name = 'Referral Program'
        verbose_name_plural = 'Referral Programs'

    def __str__(self):
        return f"Referral: ${self.referrer_reward} / ${self.referee_reward}"


class SocialProof(UUIDModel, TimeStampedModel, ActivatableModel):
    SOCIAL_TYPES = [
        ('recent_purchase', 'Recent Purchase'),
        ('stock_notification', 'Stock Notification'),
        ('review_notification', 'Review Notification'),
        ('view_count', 'View Count'),
    ]
    social_type = models.CharField(max_length=20, choices=SOCIAL_TYPES)
    message_template = models.TextField()
    min_display_count = models.PositiveIntegerField(default=5)
    display_duration_seconds = models.PositiveIntegerField(default=5)

    class Meta:
        verbose_name = 'Social Proof'
        verbose_name_plural = 'Social Proof'

    def __str__(self):
        return self.get_social_type_display()
