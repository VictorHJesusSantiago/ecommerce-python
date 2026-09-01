import uuid
from django.db import models
from django.utils.text import slugify
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']


class UUIDModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class SluggedModel(models.Model):
    slug = models.SlugField(max_length=255, unique=True, db_index=True)

    class Meta:
        abstract = True

    def generate_slug(self, source_field):
        base_slug = slugify(source_field)
        slug = base_slug
        counter = 1
        while self.__class__.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        return slug


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

    def hard_delete(self):
        return super().get_queryset().filter(is_deleted=True)


class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at', 'updated_at'])

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=['is_deleted', 'deleted_at', 'updated_at'])


class ActivatableModel(models.Model):
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        abstract = True

    def activate(self):
        self.is_active = True
        self.save(update_fields=['is_active', 'updated_at'])

    def deactivate(self):
        self.is_active = False
        self.save(update_fields=['is_active', 'updated_at'])


class OrderableModel(models.Model):
    sort_order = models.IntegerField(default=0, db_index=True)

    class Meta:
        abstract = True
        ordering = ['sort_order']


class MoneyModel(models.Model):
    currency = models.CharField(max_length=3, default='USD')

    class Meta:
        abstract = True

    def format_price(self, amount):
        from .utils import format_currency
        return format_currency(amount, self.currency)


class SEOModel(models.Model):
    meta_title = models.CharField(max_length=255, blank=True, default='')
    meta_description = models.TextField(blank=True, default='')
    meta_keywords = models.CharField(max_length=255, blank=True, default='')

    class Meta:
        abstract = True


class ImageModel(models.Model):
    image = models.ImageField(upload_to='uploads/%Y/%m/')
    alt_text = models.CharField(max_length=255, blank=True, default='')
    title = models.CharField(max_length=255, blank=True, default='')
    sort_order = models.IntegerField(default=0)

    class Meta:
        abstract = True
        ordering = ['sort_order']


class TrackableModel(models.Model):
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, default='')

    class Meta:
        abstract = True


class SiteSettings(TimeStampedModel):
    site_name = models.CharField(max_length=200, default='E-Commerce Store')
    tagline = models.CharField(max_length=300, blank=True, default='')
    site_description = models.TextField(blank=True, default='')
    logo = models.ImageField(upload_to='site/', blank=True, null=True)
    favicon = models.ImageField(upload_to='site/', blank=True, null=True)
    currency = models.CharField(max_length=3, default='USD')
    currency_symbol = models.CharField(max_length=5, default='$')
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=5.99)
    free_shipping_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=50.00)
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    max_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=10000.00)
    contact_email = models.EmailField(blank=True, default='')
    contact_phone = models.CharField(max_length=20, blank=True, default='')
    address_line1 = models.CharField(max_length=255, blank=True, default='')
    address_line2 = models.CharField(max_length=255, blank=True, default='')
    city = models.CharField(max_length=100, blank=True, default='')
    state = models.CharField(max_length=100, blank=True, default='')
    postal_code = models.CharField(max_length=20, blank=True, default='')
    country = models.CharField(max_length=2, default='US')
    facebook_url = models.URLField(blank=True, default='')
    twitter_url = models.URLField(blank=True, default='')
    instagram_url = models.URLField(blank=True, default='')
    youtube_url = models.URLField(blank=True, default='')
    google_analytics_id = models.CharField(max_length=50, blank=True, default='')
    maintenance_mode = models.BooleanField(default=False)
    maintenance_message = models.TextField(blank=True, default='We are currently under maintenance. Please check back later.')

    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        from django.core.cache import cache
        cache.delete('site_settings')
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        from django.core.cache import cache
        settings_obj = cache.get('site_settings')
        if settings_obj is None:
            settings_obj = cls.objects.first()
            if settings_obj is None:
                settings_obj = cls.objects.create()
            cache.set('site_settings', settings_obj, 300)
        return settings_obj
