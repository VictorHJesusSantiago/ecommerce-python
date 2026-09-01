from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'cart'

router = DefaultRouter()
router.register(r'saved-items', views.SavedItemViewSet, basename='saved-item')

urlpatterns = [
    path('cart/', views.CartViewSet.as_view({'get': 'list'}), name='cart-detail'),
    path('cart/add-item/', views.CartViewSet.as_view({'post': 'add_item'}), name='cart-add-item'),
    path('cart/update-item/', views.CartViewSet.as_view({'post': 'update_item'}), name='cart-update-item'),
    path('cart/remove-item/', views.CartViewSet.as_view({'post': 'remove_item'}), name='cart-remove-item'),
    path('cart/apply-coupon/', views.CartViewSet.as_view({'post': 'apply_coupon'}), name='cart-apply-coupon'),
    path('cart/remove-coupon/', views.CartViewSet.as_view({'post': 'remove_coupon'}), name='cart-remove-coupon'),
    path('cart/clear/', views.CartViewSet.as_view({'post': 'clear'}), name='cart-clear'),
    path('cart/summary/', views.CartViewSet.as_view({'get': 'summary'}), name='cart-summary'),
    path('', include(router.urls)),
]
