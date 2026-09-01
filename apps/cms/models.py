from django.db import models
from django.utils.text import slugify
from apps.common.models import TimeStampedModel, UUIDModel, SEOModel, ActivatableModel


class Page(UUIDModel, TimeStampedModel, SEOModel, ActivatableModel):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    content = models.TextField(blank=True, default='')
    template = models.CharField(max_length=100, default='cms/default.html')
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    featured_image = models.ImageField(upload_to='cms/pages/', blank=True, null=True)
    author = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL,
        null=True, blank=True
    )
    parent = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.CASCADE, related_name='children'
    )
    sort_order = models.IntegerField(default=0)
    show_in_menu = models.BooleanField(default=True)
    menu_label = models.CharField(max_length=100, blank=True, default='')

    class Meta:
        verbose_name = 'Page'
        verbose_name_plural = 'Pages'
        ordering = ['sort_order', 'title']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            counter = 1
            while Page.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{slugify(self.title)}-{counter}"
                counter += 1
        super().save(*args, **kwargs)


class MenuItem(UUIDModel):
    menu = models.ForeignKey('Menu', on_delete=models.CASCADE, related_name='items')
    parent = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.CASCADE, related_name='children'
    )
    title = models.CharField(max_length=200)
    url = models.CharField(max_length=500, blank=True, default='')
    page = models.ForeignKey(
        Page, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    target = models.CharField(
        max_length=20,
        choices=[('_self', 'Same Window'), ('_blank', 'New Window')],
        default='_self'
    )
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    css_class = models.CharField(max_length=100, blank=True, default='')

    class Meta:
        verbose_name = 'Menu Item'
        verbose_name_plural = 'Menu Items'
        ordering = ['sort_order']

    def __str__(self):
        return self.title

    @property
    def effective_url(self):
        if self.page:
            return f'/pages/{self.page.slug}/'
        return self.url or '#'


class Menu(UUIDModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Menu'
        verbose_name_plural = 'Menus'

    def __str__(self):
        return self.name


class FAQ(UUIDModel, ActivatableModel):
    question = models.CharField(max_length=500)
    answer = models.TextField()
    category = models.CharField(max_length=100, blank=True, default='general')
    sort_order = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'
        ordering = ['sort_order']

    def __str__(self):
        return self.question


class Testimonial(UUIDModel, ActivatableModel):
    customer_name = models.CharField(max_length=200)
    customer_title = models.CharField(max_length=200, blank=True, default='')
    customer_image = models.ImageField(upload_to='cms/testimonials/', blank=True, null=True)
    content = models.TextField()
    rating = models.PositiveIntegerField(default=5)
    sort_order = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Testimonial'
        verbose_name_plural = 'Testimonials'
        ordering = ['sort_order']

    def __str__(self):
        return f"{self.customer_name} - {self.rating}/5"


class Partner(UUIDModel, ActivatableModel):
    name = models.CharField(max_length=200)
    logo = models.ImageField(upload_to='cms/partners/')
    website = models.URLField(blank=True, default='')
    description = models.TextField(blank=True, default='')
    sort_order = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Partner'
        verbose_name_plural = 'Partners'
        ordering = ['sort_order']

    def __str__(self):
        return self.name


class ContactMessage(UUIDModel, TimeStampedModel):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('read', 'Read'),
        ('replied', 'Replied'),
        ('archived', 'Archived'),
    ]
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, default='')
    subject = models.CharField(max_length=300)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    replied_at = models.DateTimeField(null=True, blank=True)
    replied_by = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='replied_messages'
    )

    class Meta:
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject}"


class Subscriber(UUIDModel, TimeStampedModel):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100, blank=True, default='')
    is_active = models.BooleanField(default=True)
    source = models.CharField(max_length=50, default='website')

    class Meta:
        verbose_name = 'Subscriber'
        verbose_name_plural = 'Subscribers'

    def __str__(self):
        return self.email
