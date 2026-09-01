from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'cms'

router = DefaultRouter()
router.register(r'pages', views.PageViewSet, basename='page')
router.register(r'menus', views.MenuViewSet, basename='menu')
router.register(r'faqs', views.FAQViewSet, basename='faq')
router.register(r'testimonials', views.TestimonialViewSet, basename='testimonial')
router.register(r'partners', views.PartnerViewSet, basename='partner')
router.register(r'contact-messages', views.ContactMessageViewSet, basename='contact-message')
router.register(r'subscribers', views.SubscriberViewSet, basename='subscriber')

urlpatterns = [
    path('', include(router.urls)),
]
