from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'notifications'

router = DefaultRouter()
router.register(r'notifications', views.NotificationViewSet, basename='notification')
router.register(r'email-templates', views.EmailTemplateViewSet, basename='email-template')
router.register(r'sms-logs', views.SMSLogViewSet, basename='sms-log')
router.register(r'push-logs', views.PushNotificationLogViewSet, basename='push-log')

urlpatterns = [
    path('notification-preferences/', views.NotificationPreferenceView.as_view(), name='notification-preferences'),
    path('', include(router.urls)),
]
