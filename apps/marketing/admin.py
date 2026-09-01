from django.contrib import admin
from .models import (
    Coupon, CouponUsage, Promotion, Banner, Newsletter,
    EmailCampaign, LoyaltyProgram, ReferralProgram, SocialProof
)


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'discount_value', 'times_used', 'max_uses', 'is_active', 'start_date', 'end_date']
    list_filter = ['discount_type', 'is_active', 'is_combinable']
    search_fields = ['code', 'description']
    filter_horizontal = ['applicable_products', 'applicable_categories', 'exclude_products']
    readonly_fields = ['times_used']


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ['coupon', 'user', 'order', 'discount_amount', 'created_at']
    search_fields = ['coupon__code', 'user__email', 'order__order_number']


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ['name', 'promotion_type', 'discount_value', 'is_active', 'start_date', 'end_date', 'times_used']
    list_filter = ['promotion_type', 'is_active']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['products']
    readonly_fields = ['times_used']


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'banner_type', 'sort_order', 'is_active', 'impressions', 'clicks', 'start_date', 'end_date']
    list_filter = ['banner_type', 'is_active']
    search_fields = ['title']
    readonly_fields = ['impressions', 'clicks']


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['email', 'user', 'is_active', 'confirmed', 'source', 'subscribed_at']
    list_filter = ['is_active', 'confirmed', 'source']
    search_fields = ['email']


@admin.register(EmailCampaign)
class EmailCampaignAdmin(admin.ModelAdmin):
    list_display = ['name', 'subject', 'status', 'total_sent', 'total_opened', 'total_clicked', 'sent_at']
    list_filter = ['status']
    search_fields = ['name', 'subject']


@admin.register(LoyaltyProgram)
class LoyaltyProgramAdmin(admin.ModelAdmin):
    list_display = ['name', 'points_per_dollar', 'redemption_rate', 'min_points_redeem', 'is_active']


@admin.register(ReferralProgram)
class ReferralProgramAdmin(admin.ModelAdmin):
    list_display = ['referrer_reward', 'referee_reward', 'min_purchase_amount', 'max_referrals', 'is_active']


@admin.register(SocialProof)
class SocialProofAdmin(admin.ModelAdmin):
    list_display = ['social_type', 'min_display_count', 'display_duration_seconds', 'is_active']
    list_filter = ['social_type', 'is_active']
