from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from mptt.models import MPTTModel, TreeForeignKey
from taggit.managers import TaggableManager
from parler.models import TranslatableModel, TranslatedFields
from apps.common.models import (
    TimeStampedModel, UUIDModel, SluggedModel, SoftDeleteModel,
    ActivatableModel, SEOModel, ImageModel, OrderableModel
)


class Category(TranslatableModel, MPTTModel, UUIDModel, TimeStampedModel, SEOModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=255),
        description=models.TextField(blank=True, default=''),
        meta_title=models.CharField(max_length=255, blank=True, default=''),
        meta_description=models.TextField(blank=True, default=''),
    )
    parent = TreeForeignKey(
        'self', null=True, blank=True,
        on_delete=models.CASCADE, related_name='children'
    )
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    image = models.ImageField(upload_to='categories/%Y/%m/', blank=True, null=True)
    icon = models.CharField(max_length=100, blank=True, default='')
    is_active = models.BooleanField(default=True, db_index=True)
    sort_order = models.IntegerField(default=0, db_index=True)
    show_in_menu = models.BooleanField(default=True)
    product_count = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=0)
    lft = models.PositiveIntegerField(default=0)
    rght = models.PositiveIntegerField(default=0)
    tree_id = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['sort_order', 'name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active', 'sort_order']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            counter = 1
            while Category.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{slugify(self.name)}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    @property
    def ancestors_names(self):
        return ' > '.join([a.name for a in self.get_ancestors()])

    def update_product_count(self):
        self.product_count = self.products.filter(is_active=True).count()
        self.save(update_fields=['product_count'])


class Brand(TranslatableModel, UUIDModel, TimeStampedModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=255),
        description=models.TextField(blank=True, default=''),
    )
    slug = models.SlugField(max_length=255, unique=True)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)
    website = models.URLField(blank=True, default='')
    is_active = models.BooleanField(default=True)
    product_count = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Brand'
        verbose_name_plural = 'Brands'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class ProductCollection(TranslatableModel, UUIDModel, TimeStampedModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=255),
        description=models.TextField(blank=True, default=''),
    )
    slug = models.SlugField(max_length=255, unique=True)
    image = models.ImageField(upload_to='collections/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    products = models.ManyToManyField('Product', blank=True, related_name='collections')

    class Meta:
        verbose_name = 'Product Collection'
        verbose_name_plural = 'Product Collections'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name


class Product(TranslatableModel, UUIDModel, TimeStampedModel, SoftDeleteModel, SEOModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=500),
        description=models.TextField(blank=True, default=''),
        short_description=models.CharField(max_length=500, blank=True, default=''),
    )
    slug = models.SlugField(max_length=500, unique=True, db_index=True)
    sku = models.CharField(max_length=50, unique=True, db_index=True)
    barcode = models.CharField(max_length=50, blank=True, default='', db_index=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='products'
    )
    brand = models.ForeignKey(
        Brand, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='products'
    )
    vendor = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='products'
    )
    product_type = models.CharField(
        max_length=20,
        choices=[
            ('simple', 'Simple'),
            ('variable', 'Variable'),
            ('digital', 'Digital'),
            ('service', 'Service'),
        ],
        default='simple'
    )
    price = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    compare_at_price = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    cost_price = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    track_inventory = models.BooleanField(default=True)
    quantity = models.IntegerField(default=0)
    low_stock_threshold = models.IntegerField(default=5)
    allow_backorder = models.BooleanField(default=False)
    weight = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        help_text='Weight in kg'
    )
    length = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    width = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    height = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    is_featured = models.BooleanField(default=False, db_index=True)
    is_digital = models.BooleanField(default=False)
    is_taxable = models.BooleanField(default=True)
    tax_class = models.CharField(max_length=50, default='standard')
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Draft'),
            ('active', 'Active'),
            ('archived', 'Archived'),
        ],
        default='draft',
        db_index=True
    )
    views_count = models.PositiveIntegerField(default=0)
    sold_count = models.PositiveIntegerField(default=0)
    rating_avg = models.DecimalField(
        max_digits=3, decimal_places=2, default=Decimal('0.00')
    )
    rating_count = models.PositiveIntegerField(default=0)
    tags = TaggableManager(blank=True)
    related_products = models.ManyToManyField(
        'self', blank=True, symmetrical=True
    )
    up_sells = models.ManyToManyField(
        'self', blank=True, symmetrical=False, related_name='up_selled_by'
    )
    cross_sells = models.ManyToManyField(
        'self', blank=True, symmetrical=False, related_name='cross_selled_by'
    )
    meta_title = models.CharField(max_length=255, blank=True, default='')
    meta_description = models.TextField(blank=True, default='')
    sort_order = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-is_featured', 'sort_order', '-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['sku']),
            models.Index(fields=['status', 'is_active']),
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['price']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            counter = 1
            while Product.all_objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{slugify(self.name)}-{counter}"
                counter += 1
        if not self.sku:
            from apps.common.utils import generate_sku
            self.sku = generate_sku(hash(str(self.name)) % 999999)
        super().save(*args, **kwargs)

    @property
    def is_in_stock(self):
        if not self.track_inventory:
            return True
        if self.variants.exists():
            return any(v.is_in_stock for v in self.variants.all())
        return self.quantity > 0 or self.allow_backorder

    @property
    def is_on_sale(self):
        return self.compare_at_price and self.compare_at_price > self.price

    @property
    def discount_percentage(self):
        if self.is_on_sale:
            return round((1 - self.price / self.compare_at_price) * 100)
        return 0

    @property
    def lowest_variant_price(self):
        variants = self.variants.filter(is_active=True)
        if variants.exists():
            return variants.order_by('price').first().price
        return self.price

    @property
    def highest_variant_price(self):
        variants = self.variants.filter(is_active=True)
        if variants.exists():
            return variants.order_by('-price').first().price
        return self.price

    def increment_sold_count(self, quantity=1):
        self.sold_count += quantity
        self.save(update_fields=['sold_count', 'updated_at'])

    def increment_views(self):
        self.views_count += 1
        self.save(update_fields=['views_count'])

    def get_average_rating(self):
        reviews = self.reviews.filter(is_approved=True)
        if reviews.exists():
            from django.db.models import Avg
            return reviews.aggregate(avg=Avg('rating'))['avg'] or Decimal('0.00')
        return Decimal('0.00')

    def update_rating(self):
        self.rating_avg = self.get_average_rating()
        self.rating_count = self.reviews.filter(is_approved=True).count()
        self.save(update_fields=['rating_avg', 'rating_count', 'updated_at'])


class ProductVariant(UUIDModel, TimeStampedModel, ActivatableModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=50, unique=True, db_index=True)
    price = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    compare_at_price = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    quantity = models.IntegerField(default=0)
    low_stock_threshold = models.IntegerField(default=5)
    weight = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    barcode = models.CharField(max_length=50, blank=True, default='')
    image = models.ImageField(upload_to='variants/', blank=True, null=True)
    sort_order = models.IntegerField(default=0)
    options = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = 'Product Variant'
        verbose_name_plural = 'Product Variants'
        ordering = ['sort_order', 'name']
        unique_together = ['product', 'name']

    def __str__(self):
        return f"{self.product.name} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.sku:
            from apps.common.utils import generate_sku
            self.sku = generate_sku(
                hash(str(self.product_id)) % 999999,
                hash(str(self.name)) % 999
            )
        super().save(*args, **kwargs)

    @property
    def is_in_stock(self):
        return self.quantity > 0

    @property
    def is_on_sale(self):
        return self.compare_at_price and self.compare_at_price > self.price


class ProductImage(UUIDModel, TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/%Y/%m/')
    alt_text = models.CharField(max_length=255, blank=True, default='')
    title = models.CharField(max_length=255, blank=True, default='')
    is_primary = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Product Image'
        verbose_name_plural = 'Product Images'
        ordering = ['-is_primary', 'sort_order']

    def __str__(self):
        return f"Image for {self.product.name}"

    def save(self, *args, **kwargs):
        if self.is_primary:
            ProductImage.objects.filter(
                product=self.product, is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)


class ProductAttribute(UUIDModel, TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('number', 'Number'),
            ('select', 'Select'),
            ('multiselect', 'Multi-Select'),
            ('boolean', 'Boolean'),
            ('date', 'Date'),
        ],
        default='text'
    )
    is_required = models.BooleanField(default=False)
    is_filterable = models.BooleanField(default=False)
    is_variant = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Product Attribute'
        verbose_name_plural = 'Product Attributes'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class ProductAttributeValue(UUIDModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='attribute_values')
    attribute = models.ForeignKey(ProductAttribute, on_delete=models.CASCADE, related_name='values')
    value = models.CharField(max_length=500)

    class Meta:
        verbose_name = 'Product Attribute Value'
        verbose_name_plural = 'Product Attribute Values'
        unique_together = ['product', 'attribute']

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"


class VariantAttributeValue(UUIDModel):
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='attribute_values')
    attribute = models.ForeignKey(ProductAttribute, on_delete=models.CASCADE, related_name='variant_values')
    value = models.CharField(max_length=500)

    class Meta:
        verbose_name = 'Variant Attribute Value'
        verbose_name_plural = 'Variant Attribute Values'
        unique_together = ['variant', 'attribute']

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"


class ProductRecommendation(UUIDModel):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='recommendations_from'
    )
    recommended = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='recommendations_to'
    )
    ranking = models.PositiveIntegerField(default=0)
    recommendation_type = models.CharField(
        max_length=20,
        choices=[
            ('similar', 'Similar'),
            ('frequently_bought_together', 'Frequently Bought Together'),
            ('customers_also_viewed', 'Customers Also Viewed'),
        ],
        default='similar'
    )

    class Meta:
        verbose_name = 'Product Recommendation'
        verbose_name_plural = 'Product Recommendations'
        ordering = ['ranking']
        unique_together = ['product', 'recommended', 'recommendation_type']
