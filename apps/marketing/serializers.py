from rest_framework import serializers
from .models import (
    Coupon, CouponUsage, Promotion, Banner, Newsletter,
    EmailCampaign, LoyaltyProgram, ReferralProgram, SocialProof
)


class CouponSerializer(serializers.ModelSerializer):
    is_valid = serializers.BooleanField(read_only=True)
    discount_type_display = serializers.CharField(source='get_discount_type_display', read_only=True)

    class Meta:
        model = Coupon
        fields = [
            'id', 'code', 'description', 'discount_type', 'discount_type_display',
            'discount_value', 'max_discount_amount', 'min_order_amount',
            'max_uses', 'max_uses_per_user', 'times_used', 'start_date',
            'end_date', 'is_active', 'is_valid', 'is_combinable', 'created_at',
        ]
        read_only_fields = ['id', 'times_used', 'created_at']


class CouponValidateSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=50)


class PromotionSerializer(serializers.ModelSerializer):
    products_count = serializers.IntegerField(read_only=True)
    is_active_promotion = serializers.BooleanField(read_only=True)

    class Meta:
        model = Promotion
        fields = [
            'id', 'name', 'slug', 'description', 'promotion_type',
            'discount_type', 'discount_value', 'start_date', 'end_date',
            'banner_image', 'priority', 'usage_limit', 'times_used',
            'is_active', 'products_count', 'is_active_promotion', 'created_at',
        ]
        read_only_fields = ['id', 'slug', 'times_used', 'created_at']


class BannerSerializer(serializers.ModelSerializer):
    is_active_banner = serializers.BooleanField(read_only=True)
    click_through_rate = serializers.FloatField(read_only=True)

    class Meta:
        model = Banner
        fields = [
            'id', 'title', 'subtitle', 'image', 'mobile_image', 'link_url',
            'banner_type', 'start_date', 'end_date', 'sort_order', 'is_active',
            'impressions', 'clicks', 'is_active_banner', 'click_through_rate',
            'created_at',
        ]
        read_only_fields = ['id', 'impressions', 'clicks', 'created_at']


class NewsletterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Newsletter
        fields = ['id', 'email', 'is_active', 'confirmed', 'source', 'subscribed_at']
        read_only_fields = ['id', 'is_active', 'confirmed', 'subscribed_at']


class EmailCampaignSerializer(serializers.ModelSerializer):
    open_rate = serializers.FloatField(read_only=True)
    click_rate = serializers.FloatField(read_only=True)

    class Meta:
        model = EmailCampaign
        fields = [
            'id', 'name', 'subject', 'preview_text', 'status',
            'scheduled_at', 'sent_at', 'total_recipients', 'total_sent',
            'total_opened', 'total_clicked', 'total_bounced', 'total_unsubscribed',
            'open_rate', 'click_rate', 'segment', 'created_at',
        ]
        read_only_fields = [
            'id', 'sent_at', 'total_recipients', 'total_sent',
            'total_opened', 'total_clicked', 'total_bounced', 'total_unsubscribed',
            'created_at',
        ]


class LoyaltyProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoyaltyProgram
        fields = ['id', 'name', 'points_per_dollar', 'redemption_rate',
                  'min_points_redeem', 'tier_thresholds', 'is_active']


class ReferralProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferralProgram
        fields = ['id', 'referrer_reward', 'referee_reward', 'min_purchase_amount',
                  'max_referrals', 'is_active']
