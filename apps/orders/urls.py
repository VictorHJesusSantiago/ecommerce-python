from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'orders'

router = DefaultRouter()
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'return-requests', views.ReturnRequestViewSet, basename='return-request')

urlpatterns = [
    path('', include(router.urls)),
    path('admin/orders/stats/', views.AdminOrderStatsView.as_view(), name='admin-order-stats'),
]
