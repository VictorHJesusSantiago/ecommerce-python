import uuid
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal
from apps.common.models import TimeStampedModel, UUIDModel, SoftDeleteModel, ActivatableModel


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set.')
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)

    def get_by_natural_key(self, email):
        return self.get(email=email)


class User(AbstractUser, UUIDModel, TimeStampedModel, SoftDeleteModel):
    email = models.EmailField(unique=True, db_index=True)
    phone_number = models.CharField(max_length=20, blank=True, default='')
    avatar = models.ImageField(upload_to='avatars/%Y/%m/', blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=10,
        choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other'), ('', 'Prefer not to say')],
        blank=True,
        default=''
    )
    role = models.CharField(
        max_length=20,
        choices=[
            ('customer', 'Customer'),
            ('vendor', 'Vendor'),
            ('admin', 'Admin'),
            ('support', 'Support'),
        ],
        default='customer'
    )
    is_email_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    phone_verified_at = models.DateTimeField(null=True, blank=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    last_active_at = models.DateTimeField(null=True, blank=True)
    login_count = models.PositiveIntegerField(default=0)
    newsletter_subscribed = models.BooleanField(default=False)
    terms_accepted = models.BooleanField(default=False)
    terms_accepted_at = models.DateTimeField(null=True, blank=True)
    referral_code = models.CharField(max_length=20, unique=True, blank=True, null=True)
    referred_by = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='referrals'
    )
    loyalty_points = models.PositiveIntegerField(default=0)
    total_spent = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    total_orders = models.PositiveIntegerField(default=0)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
            models.Index(fields=['is_email_verified']),
        ]

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if not self.referral_code:
            from apps.common.utils import generate_unique_code
            self.referral_code = generate_unique_code(8)
        super().save(*args, **kwargs)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email

    @property
    def is_vendor(self):
        return self.role == 'vendor' and hasattr(self, 'vendor_profile')

    @property
    def is_customer(self):
        return self.role == 'customer'

    def add_loyalty_points(self, points):
        self.loyalty_points += points
        self.save(update_fields=['loyalty_points', 'updated_at'])

    def deduct_loyalty_points(self, points):
        if self.loyalty_points >= points:
            self.loyalty_points -= points
            self.save(update_fields=['loyalty_points', 'updated_at'])
            return True
        return False

    def record_login(self, ip_address=None):
        self.login_count += 1
        self.last_login_ip = ip_address
        self.last_active_at = timezone.now()
        self.save(update_fields=['login_count', 'last_login_ip', 'last_active_at', 'updated_at'])


class Address(UUIDModel, TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    label = models.CharField(max_length=50, blank=True, default='Home')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    company = models.CharField(max_length=150, blank=True, default='')
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, default='')
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=2, default='US')
    phone = models.CharField(max_length=20, blank=True, default='')
    is_default = models.BooleanField(default=False)
    is_billing = models.BooleanField(default=False)
    is_shipping = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.address_line1}, {self.city}"

    def save(self, *args, **kwargs):
        if self.is_default:
            Address.objects.filter(
                user=self.user, is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        if self.is_billing:
            Address.objects.filter(
                user=self.user, is_billing=True
            ).exclude(pk=self.pk).update(is_billing=False)
        super().save(*args, **kwargs)

    @property
    def full_address(self):
        lines = [self.address_line1]
        if self.address_line2:
            lines.append(self.address_line2)
        lines.append(f"{self.city}, {self.state} {self.postal_code}")
        lines.append(self.get_country_display())
        return '\n'.join(lines)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class PaymentMethod(UUIDModel, TimeStampedModel):
    PAYMENT_TYPES = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('paypal', 'PayPal'),
        ('bank_account', 'Bank Account'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_methods')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    provider = models.CharField(max_length=50, blank=True, default='')
    last_four = models.CharField(max_length=4, blank=True, default='')
    is_default = models.BooleanField(default=False)
    billing_address = models.ForeignKey(
        Address, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='payment_methods'
    )
    token = models.CharField(max_length=500, blank=True, default='')
    expiry_month = models.PositiveIntegerField(null=True, blank=True)
    expiry_year = models.PositiveIntegerField(null=True, blank=True)
    cardholder_name = models.CharField(max_length=200, blank=True, default='')

    class Meta:
        verbose_name = 'Payment Method'
        verbose_name_plural = 'Payment Methods'
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.get_payment_type_display()} ending in {self.last_four}"

    def save(self, *args, **kwargs):
        if self.is_default:
            PaymentMethod.objects.filter(
                user=self.user, is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        if self.expiry_month and self.expiry_year:
            now = timezone.now()
            return now.year > self.expiry_year or (
                now.year == self.expiry_year and now.month > self.expiry_month
            )
        return False

    @property
    def display_name(self):
        return f"{self.provider} ****{self.last_four}"


class VendorProfile(UUIDModel, TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vendor_profile')
    shop_name = models.CharField(max_length=200)
    shop_description = models.TextField(blank=True, default='')
    shop_logo = models.ImageField(upload_to='vendor/logos/', blank=True, null=True)
    shop_banner = models.ImageField(upload_to='vendor/banners/', blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    approved_at = models.DateTimeField(null=True, blank=True)
    commission_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal('10.00')
    )
    total_sales = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0.00')
    )
    total_products = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(
        max_digits=3, decimal_places=2, default=Decimal('0.00')
    )
    tax_id = models.CharField(max_length=50, blank=True, default='')
    business_type = models.CharField(max_length=50, blank=True, default='')
    website = models.URLField(blank=True, default='')
    shipping_policy = models.TextField(blank=True, default='')
    return_policy = models.TextField(blank=True, default='')
    avg_processing_time = models.CharField(max_length=50, blank=True, default='1-3 business days')

    class Meta:
        verbose_name = 'Vendor Profile'
        verbose_name_plural = 'Vendor Profiles'

    def __str__(self):
        return self.shop_name

    def approve(self):
        self.is_approved = True
        self.approved_at = timezone.now()
        self.save(update_fields=['is_approved', 'approved_at', 'updated_at'])
        self.user.role = 'vendor'
        self.user.save(update_fields=['role', 'updated_at'])


class UserActivity(UUIDModel, TimeStampedModel):
    ACTION_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('view_product', 'View Product'),
        ('add_to_cart', 'Add to Cart'),
        ('purchase', 'Purchase'),
        ('review', 'Review'),
        ('wishlist', 'Wishlist'),
        ('search', 'Search'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField(blank=True, default='')
    metadata = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        verbose_name = 'User Activity'
        verbose_name_plural = 'User Activities'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'action']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.get_action_display()}"

    @classmethod
    def log(cls, user, action, description='', metadata=None, ip_address=None):
        return cls.objects.create(
            user=user,
            action=action,
            description=description,
            metadata=metadata or {},
            ip_address=ip_address,
        )


class UserSession(UUIDModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=255, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, default='')
    last_activity = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'User Session'
        verbose_name_plural = 'User Sessions'
        ordering = ['-last_activity']

    def __str__(self):
        return f"{self.user.email} - {self.ip_address}"

    def deactivate(self):
        self.is_active = False
        self.save(update_fields=['is_active', 'updated_at'])
