from django.contrib import admin
from .models import (
    Warehouse, StockItem, StockMovement, StockTransfer, StockTransferItem,
    Supplier, PurchaseOrder, PurchaseOrderItem, InventoryLog
)


class StockItemInline(admin.TabularInline):
    model = StockItem
    extra = 0
    fields = ['product', 'variant', 'quantity', 'reserved_quantity', 'low_stock_threshold', 'location']


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'city', 'state', 'country', 'is_active', 'priority']
    list_filter = ['is_active', 'country']
    search_fields = ['name', 'code']
    inlines = [StockItemInline]


@admin.register(StockItem)
class StockItemAdmin(admin.ModelAdmin):
    list_display = ['product', 'variant', 'warehouse', 'quantity', 'reserved_quantity', 'low_stock_threshold', 'location']
    list_filter = ['warehouse', 'product__category']
    search_fields = ['product__name', 'product__sku', 'location']
    raw_id_fields = ['product', 'variant', 'warehouse']


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['stock_item', 'movement_type', 'quantity', 'reference', 'performed_by', 'created_at']
    list_filter = ['movement_type']
    search_fields = ['stock_item__product__name', 'reference']
    readonly_fields = ['created_at']


@admin.register(StockTransfer)
class StockTransferAdmin(admin.ModelAdmin):
    list_display = ['id', 'source_warehouse', 'destination_warehouse', 'status', 'created_by', 'completed_at']
    list_filter = ['status']


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'contact_name', 'email', 'phone', 'lead_time_days', 'rating', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'code']


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 0
    readonly_fields = ['line_total']


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'supplier', 'warehouse', 'status', 'total', 'expected_delivery', 'created_at']
    list_filter = ['status']
    search_fields = ['order_number', 'supplier__name']
    inlines = [PurchaseOrderItemInline]


@admin.register(InventoryLog)
class InventoryLogAdmin(admin.ModelAdmin):
    list_display = ['product', 'warehouse', 'action', 'quantity_before', 'quantity_after', 'created_at']
    list_filter = ['action']
    search_fields = ['product__name']
    readonly_fields = ['created_at']
