from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'payments'

router = DefaultRouter()
router.register(r'gateways', views.PaymentGatewayViewSet, basename='gateway')
router.register(r'transactions', views.TransactionViewSet, basename='transaction')
router.register(r'refunds', views.RefundViewSet, basename='refund')
router.register(r'payment-methods', views.PaymentMethodViewSet, basename='payment-method')
router.register(r'webhooks', views.WebhookViewSet, basename='webhook')

urlpatterns = [
    path('', include(router.urls)),
]
