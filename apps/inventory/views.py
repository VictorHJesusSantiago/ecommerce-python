from rest_framework import viewsets, status, permissions, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Q, F

from .models import (
    Warehouse, StockItem, StockMovement, StockTransfer,
    Supplier, PurchaseOrder, InventoryLog
)
from .serializers import (
    WarehouseSerializer, StockItemSerializer, StockMovementSerializer,
    StockAdjustSerializer, StockTransferSerializer, SupplierSerializer,
    PurchaseOrderSerializer, InventoryLogSerializer, LowStockReportSerializer
)
from apps.common.permissions import IsAdminUser, CanManageInventory
from apps.common.pagination import StandardResultsSetPagination
from apps.common.exceptions import InventoryError


class WarehouseViewSet(viewsets.ModelViewSet):
    serializer_class = WarehouseSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Warehouse.objects.filter(is_active=True)

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [CanManageInventory()]


class StockItemViewSet(viewsets.ModelViewSet):
    serializer_class = StockItemSerializer
    permission_classes = [CanManageInventory]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        qs = StockItem.objects.select_related('product', 'warehouse')
        product = self.request.query_params.get('product')
        warehouse = self.request.query_params.get('warehouse')
        low_stock = self.request.query_params.get('low_stock')
        if product:
            qs = qs.filter(product_id=product)
        if warehouse:
            qs = qs.filter(warehouse_id=warehouse)
        if low_stock and low_stock.lower() == 'true':
            qs = qs.filter(quantity__lte=F('low_stock_threshold'))
        return qs

    @action(detail=False, methods=['post'])
    def adjust_stock(self, request):
        serializer = StockAdjustSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            stock_item = StockItem.objects.get(pk=serializer.validated_data['stock_item_id'])
        except StockItem.DoesNotExist:
            raise InventoryError(detail='Stock item not found.')

        old_qty, new_qty = stock_item.adjust_stock(
            serializer.validated_data['quantity_change'],
            reason=serializer.validated_data['reason'],
            performed_by=request.user,
        )

        return Response({
            'success': True,
            'message': f'Stock adjusted from {old_qty} to {new_qty}.',
            'old_quantity': old_qty,
            'new_quantity': new_qty,
        })

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        qs = StockItem.objects.filter(
            quantity__lte=F('low_stock_threshold'),
            product__is_active=True
        ).select_related('product', 'warehouse')
        serializer = StockItemSerializer(qs, many=True)
        return Response({'success': True, 'items': serializer.data})

    @action(detail=False, methods=['get'])
    def summary(self, request):
        total_products = StockItem.objects.values('product').distinct().count()
        total_stock_value = StockItem.objects.aggregate(
            value=Sum(F('quantity') * F('cost_price'))
        )['value'] or 0
        low_stock_count = StockItem.objects.filter(
            quantity__lte=F('low_stock_threshold')
        ).count()
        out_of_stock = StockItem.objects.filter(quantity=0).count()

        return Response({
            'success': True,
            'summary': {
                'total_products_tracked': total_products,
                'total_stock_value': str(total_stock_value),
                'low_stock_items': low_stock_count,
                'out_of_stock_items': out_of_stock,
            }
        })


class StockMovementViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = StockMovementSerializer
    permission_classes = [CanManageInventory]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        qs = StockMovement.objects.select_related('stock_item__product', 'stock_item__warehouse')
        stock_item = self.request.query_params.get('stock_item')
        movement_type = self.request.query_params.get('movement_type')
        if stock_item:
            qs = qs.filter(stock_item_id=stock_item)
        if movement_type:
            qs = qs.filter(movement_type=movement_type)
        return qs


class StockTransferViewSet(viewsets.ModelViewSet):
    serializer_class = StockTransferSerializer
    permission_classes = [CanManageInventory]

    def get_queryset(self):
        return StockTransfer.objects.prefetch_related('items')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        transfer = self.get_object()
        if transfer.status != 'in_transit':
            return Response({
                'success': False,
                'error': {'message': 'Transfer must be in transit to complete.'}
            }, status=400)

        for item in transfer.items.all():
            source_stock = StockItem.objects.filter(
                product=item.product, variant=item.variant,
                warehouse=transfer.source_warehouse
            ).first()
            dest_stock, _ = StockItem.objects.get_or_create(
                product=item.product, variant=item.variant,
                warehouse=transfer.destination_warehouse,
                defaults={'quantity': 0}
            )

            if source_stock and source_stock.quantity >= item.quantity:
                source_stock.quantity -= item.quantity
                source_stock.save(update_fields=['quantity'])
                dest_stock.quantity += item.quantity
                dest_stock.save(update_fields=['quantity'])

        transfer.status = 'completed'
        from django.utils import timezone
        transfer.completed_at = timezone.now()
        transfer.save(update_fields=['status', 'completed_at', 'updated_at'])

        return Response({'success': True, 'message': 'Transfer completed.'})


class SupplierViewSet(viewsets.ModelViewSet):
    serializer_class = SupplierSerializer
    permission_classes = [CanManageInventory]

    def get_queryset(self):
        return Supplier.objects.filter(is_active=True)


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    serializer_class = PurchaseOrderSerializer
    permission_classes = [CanManageInventory]

    def get_queryset(self):
        qs = PurchaseOrder.objects.prefetch_related('items')
        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs

    def perform_create(self, serializer):
        from apps.common.utils import generate_unique_code
        serializer.save(
            created_by=self.request.user,
            order_number=generate_unique_code(8)
        )

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        po = self.get_object()
        if po.status != 'draft':
            return Response({'success': False, 'error': {'message': 'Only draft POs can be submitted.'}}, status=400)
        po.status = 'submitted'
        po.save(update_fields=['status', 'updated_at'])
        return Response({'success': True, 'message': 'PO submitted.'})

    @action(detail=True, methods=['post'])
    def receive(self, request, pk=None):
        po = self.get_object()
        if po.status not in ('confirmed', 'shipped'):
            return Response({'success': False, 'error': {'message': 'PO cannot be received.'}}, status=400)

        for item in po.items.all():
            received_qty = item.received_quantity
            if received_qty > 0:
                stock_item, _ = StockItem.objects.get_or_create(
                    product=item.product, variant=item.variant,
                    warehouse=po.warehouse,
                    defaults={'quantity': 0}
                )
                stock_item.quantity += received_qty
                stock_item.save(update_fields=['quantity'])
                StockMovement.objects.create(
                    stock_item=stock_item,
                    movement_type='purchase',
                    quantity=received_qty,
                    reference=f'PO-{po.order_number}',
                    performed_by=request.user,
                )

        from django.utils import timezone
        po.status = 'received'
        po.received_at = timezone.now()
        po.save(update_fields=['status', 'received_at', 'updated_at'])
        return Response({'success': True, 'message': 'PO received and stock updated.'})


class InventoryLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = InventoryLogSerializer
    permission_classes = [CanManageInventory]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return InventoryLog.objects.select_related('product', 'warehouse')
