from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'marketing'

router = DefaultRouter()
router.register(r'coupons', views.CouponViewSet, basename='coupon')
router.register(r'promotions', views.PromotionViewSet, basename='promotion')
router.register(r'banners', views.BannerViewSet, basename='banner')
router.register(r'newsletters', views.NewsletterViewSet, basename='newsletter')
router.register(r'email-campaigns', views.EmailCampaignViewSet, basename='email-campaign')
router.register(r'loyalty-programs', views.LoyaltyProgramViewSet, basename='loyalty-program')
router.register(r'referral-programs', views.ReferralProgramViewSet, basename='referral-program')

urlpatterns = [
    path('', include(router.urls)),
]
