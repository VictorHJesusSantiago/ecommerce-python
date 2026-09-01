from django import forms
from .models import Coupon, Promotion, Banner, Newsletter, EmailCampaign


class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code', 'description', 'discount_type', 'discount_value',
                  'max_discount_amount', 'min_order_amount', 'max_uses',
                  'max_uses_per_user', 'start_date', 'end_date', 'is_active',
                  'is_combinable']
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class PromotionForm(forms.ModelForm):
    class Meta:
        model = Promotion
        fields = ['name', 'slug', 'description', 'promotion_type', 'discount_type',
                  'discount_value', 'start_date', 'end_date', 'banner_image',
                  'priority', 'usage_limit', 'is_active']
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        prepopulated_fields = {'slug': ('name',)}


class BannerForm(forms.ModelForm):
    class Meta:
        model = Banner
        fields = ['title', 'subtitle', 'image', 'mobile_image', 'link_url',
                  'banner_type', 'start_date', 'end_date', 'sort_order', 'is_active']
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = ['email', 'source', 'is_active']


class EmailCampaignForm(forms.ModelForm):
    class Meta:
        model = EmailCampaign
        fields = ['name', 'subject', 'preview_text', 'html_content',
                  'plain_text_content', 'scheduled_at', 'segment']
        widgets = {
            'html_content': forms.Textarea(attrs={'rows': 10}),
            'plain_text_content': forms.Textarea(attrs={'rows': 5}),
            'scheduled_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
