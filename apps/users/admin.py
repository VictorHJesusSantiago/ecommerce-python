from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from .models import Address, PaymentMethod, VendorProfile, UserActivity, UserSession

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'role', 'is_active', 'is_email_verified', 'loyalty_points', 'created_at']
    list_filter = ['role', 'is_active', 'is_email_verified', 'is_staff']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['-created_at']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('phone_number', 'avatar', 'date_of_birth', 'gender', 'role',
                       'is_email_verified', 'is_phone_verified', 'newsletter_subscribed',
                       'loyalty_points', 'total_spent', 'total_orders', 'referral_code',
                       'referred_by', 'last_login_ip', 'last_active_at', 'login_count')
        }),
    )
    readonly_fields = ['loyalty_points', 'total_spent', 'total_orders', 'login_count', 'created_at', 'updated_at']


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'label', 'first_name', 'last_name', 'city', 'state', 'country', 'is_default']
    list_filter = ['country', 'is_default', 'is_billing', 'is_shipping']
    search_fields = ['user__email', 'first_name', 'last_name', 'city']
    raw_id_fields = ['user']


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['user', 'payment_type', 'provider', 'last_four', 'is_default']
    list_filter = ['payment_type', 'provider', 'is_default']
    search_fields = ['user__email', 'cardholder_name']
    raw_id_fields = ['user', 'billing_address']


@admin.register(VendorProfile)
class VendorProfileAdmin(admin.ModelAdmin):
    list_display = ['shop_name', 'user', 'is_approved', 'total_sales', 'rating', 'created_at']
    list_filter = ['is_approved', 'business_type']
    search_fields = ['shop_name', 'user__email']
    raw_id_fields = ['user']
    actions = ['approve_vendors']

    def approve_vendors(self, request, queryset):
        for vendor in queryset.filter(is_approved=False):
            vendor.approve()
        self.message_user(request, f"Approved {queryset.count()} vendors.")
    approve_vendors.short_description = "Approve selected vendors"


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'description', 'ip_address', 'created_at']
    list_filter = ['action']
    search_fields = ['user__email', 'description']
    raw_id_fields = ['user']
    readonly_fields = ['created_at']


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'ip_address', 'is_active', 'last_activity', 'created_at']
    list_filter = ['is_active']
    search_fields = ['user__email', 'ip_address']
    raw_id_fields = ['user']
    readonly_fields = ['created_at', 'last_activity']
