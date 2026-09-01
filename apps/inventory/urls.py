from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'inventory'

router = DefaultRouter()
router.register(r'warehouses', views.WarehouseViewSet, basename='warehouse')
router.register(r'stock-items', views.StockItemViewSet, basename='stock-item')
router.register(r'stock-movements', views.StockMovementViewSet, basename='stock-movement')
router.register(r'stock-transfers', views.StockTransferViewSet, basename='stock-transfer')
router.register(r'suppliers', views.SupplierViewSet, basename='supplier')
router.register(r'purchase-orders', views.PurchaseOrderViewSet, basename='purchase-order')
router.register(r'inventory-logs', views.InventoryLogViewSet, basename='inventory-log')

urlpatterns = [
    path('', include(router.urls)),
]
