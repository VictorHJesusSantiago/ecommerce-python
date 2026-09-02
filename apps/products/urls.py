from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'products'

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'brands', views.BrandViewSet, basename='brand')
router.register(r'collections', views.ProductCollectionViewSet, basename='collection')
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'attributes', views.ProductAttributeViewSet, basename='attribute')

urlpatterns = [
    path('', include(router.urls)),
    path('products/<uuid:product_pk>/variants/',
         views.ProductVariantViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='product-variants'),
    path('products/<uuid:product_pk>/variants/<uuid:pk>/',
         views.ProductVariantViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}),
         name='product-variant-detail'),
]
