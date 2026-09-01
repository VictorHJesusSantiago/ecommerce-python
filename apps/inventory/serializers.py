from rest_framework import serializers
from .models import (
    Warehouse, StockItem, StockMovement, StockTransfer, StockTransferItem,
    Supplier, PurchaseOrder, PurchaseOrderItem, InventoryLog
)
from apps.products.serializers import ProductListSerializer


class WarehouseSerializer(serializers.ModelSerializer):
    total_items = serializers.IntegerField(read_only=True)

    class Meta:
        model = Warehouse
        fields = [
            'id', 'name', 'code', 'address_line1', 'address_line2', 'city',
            'state', 'postal_code', 'country', 'phone', 'email', 'manager',
            'priority', 'shipping_cost_per_kg', 'is_active', 'total_items',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class StockItemSerializer(serializers.ModelSerializer):
    product_detail = ProductListSerializer(source='product', read_only=True)
    available_quantity = serializers.IntegerField(read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    needs_reorder = serializers.BooleanField(read_only=True)

    class Meta:
        model = StockItem
        fields = [
            'id', 'product', 'product_detail', 'variant', 'warehouse',
            'quantity', 'reserved_quantity', 'available_quantity',
            'low_stock_threshold', 'reorder_point', 'reorder_quantity',
            'cost_price', 'location', 'is_low_stock', 'needs_reorder',
            'created_at',
        ]
        read_only_fields = ['id', 'available_quantity', 'is_low_stock', 'needs_reorder', 'created_at']


class StockMovementSerializer(serializers.ModelSerializer):
    movement_type_display = serializers.CharField(source='get_movement_type_display', read_only=True)
    product_name = serializers.CharField(source='stock_item.product.name', read_only=True)

    class Meta:
        model = StockMovement
        fields = [
            'id', 'stock_item', 'product_name', 'movement_type', 'movement_type_display',
            'quantity', 'reference', 'notes', 'performed_by', 'related_order',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class StockAdjustSerializer(serializers.Serializer):
    stock_item_id = serializers.UUIDField()
    quantity_change = serializers.IntegerField()
    reason = serializers.CharField()


class StockTransferItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockTransferItem
        fields = ['id', 'product', 'variant', 'quantity']


class StockTransferSerializer(serializers.ModelSerializer):
    items = StockTransferItemSerializer(many=True, read_only=True)
    source_warehouse_name = serializers.CharField(source='source_warehouse.name', read_only=True)
    destination_warehouse_name = serializers.CharField(source='destination_warehouse.name', read_only=True)

    class Meta:
        model = StockTransfer
        fields = [
            'id', 'source_warehouse', 'source_warehouse_name',
            'destination_warehouse', 'destination_warehouse_name',
            'status', 'notes', 'created_by', 'items', 'completed_at',
            'created_at',
        ]
        read_only_fields = ['id', 'completed_at', 'created_at']


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = [
            'id', 'name', 'code', 'contact_name', 'email', 'phone',
            'address', 'website', 'payment_terms', 'lead_time_days',
            'rating', 'is_active', 'notes', 'created_at',
        ]
        read_only_fields = ['id', 'rating', 'created_at']


class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    line_total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = PurchaseOrderItem
        fields = [
            'id', 'product', 'product_name', 'variant', 'quantity',
            'received_quantity', 'unit_cost', 'line_total',
        ]


class PurchaseOrderSerializer(serializers.ModelSerializer):
    items = PurchaseOrderItemSerializer(many=True, read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = [
            'id', 'supplier', 'supplier_name', 'warehouse', 'order_number',
            'status', 'subtotal', 'tax_amount', 'shipping_amount', 'total',
            'expected_delivery', 'notes', 'created_by', 'items',
            'received_at', 'created_at',
        ]
        read_only_fields = ['id', 'order_number', 'subtotal', 'total', 'created_at']


class InventoryLogSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = InventoryLog
        fields = [
            'id', 'product', 'product_name', 'variant', 'warehouse',
            'action', 'quantity_before', 'quantity_after', 'reference',
            'notes', 'performed_by', 'created_at',
        ]


class LowStockReportSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()
    product_name = serializers.CharField()
    sku = serializers.CharField()
    warehouse = serializers.CharField()
    quantity = serializers.IntegerField()
    threshold = serializers.IntegerField()
    available = serializers.IntegerField()
