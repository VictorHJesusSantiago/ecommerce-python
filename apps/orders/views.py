from rest_framework import viewsets, status, permissions, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Sum, Count, Avg
from django.utils import timezone

from .models import (
    Order, OrderItem, OrderStatusHistory, Shipment, ShipmentTracking,
    OrderNote, OrderPayment, ReturnRequest
)
from .serializers import (
    OrderListSerializer, OrderDetailSerializer, OrderCreateSerializer,
    OrderStatusUpdateSerializer, ShipmentCreateSerializer, ShipmentSerializer,
    ShipmentTrackingSerializer, OrderStatusHistorySerializer,
    OrderNoteSerializer, OrderPaymentSerializer, ReturnRequestSerializer,
    ReturnRequestCreateSerializer, OrderStatsSerializer
)
from apps.common.permissions import IsAdminUser, IsOrderOwnerOrAdmin, CanManageOrders
from apps.common.pagination import OrderPagination
from apps.common.signals import order_completed


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = OrderPagination

    def get_queryset(self):
        if self.request.user.is_staff:
            qs = Order.objects.all()
        else:
            qs = Order.objects.filter(user=self.request.user)

        order_status = self.request.query_params.get('status')
        if order_status:
            qs = qs.filter(status=order_status)

        payment_status = self.request.query_params.get('payment_status')
        if payment_status:
            qs = qs.filter(payment_status=payment_status)

        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            qs = qs.filter(created_at__date__gte=date_from)
        if date_to:
            qs = qs.filter(created_at__date__lte=date_to)

        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(
                Q(order_number__icontains=search) |
                Q(user__email__icontains=search)
            )
        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return OrderListSerializer
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderDetailSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from apps.cart.models import Cart
        from apps.users.models import Address
        from apps.common.utils import generate_order_number

        cart = Cart.objects.filter(user=request.user, is_active=True).first()
        if not cart or not cart.items.exists():
            return Response({
                'success': False,
                'error': {'message': 'Cart is empty.'}
            }, status=status.HTTP_400_BAD_REQUEST)

        shipping_address = Address.objects.get(
            pk=serializer.validated_data['shipping_address_id'],
            user=request.user
        )

        order = Order.objects.create(
            user=request.user,
            order_number=generate_order_number(),
            shipping_first_name=shipping_address.first_name,
            shipping_last_name=shipping_address.last_name,
            shipping_company=shipping_address.company,
            shipping_address_line1=shipping_address.address_line1,
            shipping_address_line2=shipping_address.address_line2,
            shipping_city=shipping_address.city,
            shipping_state=shipping_address.state,
            shipping_postal_code=shipping_address.postal_code,
            shipping_country=shipping_address.country,
            shipping_phone=shipping_address.phone,
            billing_same_as_shipping=True,
            coupon=cart.coupon,
            coupon_code=cart.coupon.code if cart.coupon else '',
            customer_notes=serializer.validated_data.get('customer_notes', ''),
            source='web',
            ip_address=request.META.get('REMOTE_ADDR'),
        )

        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                variant=cart_item.variant,
                product_name=cart_item.product.name,
                product_sku=cart_item.product.sku,
                variant_name=cart_item.variant.name if cart_item.variant else '',
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price,
                total_price=cart_item.line_total,
                product_snapshot={
                    'name': cart_item.product.name,
                    'sku': cart_item.product.sku,
                    'price': str(cart_item.unit_price),
                    'image': cart_item.product.images.first().image.url if cart_item.product.images.exists() else '',
                }
            )

        order.calculate_totals()
        order.calculate_shipping_amount()

        if cart.coupon:
            discount = cart.coupon.calculate_discount(order.subtotal)
            order.discount_amount = discount
            order.save(update_fields=['discount_amount', 'total'])

        cart.clear()

        OrderStatusHistory.log_status_change(order, 'pending', 'Order created')

        return Response({
            'success': True,
            'message': 'Order placed successfully.',
            'order': OrderDetailSerializer(order).data,
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if not order.can_cancel:
            return Response({
                'success': False,
                'error': {'message': 'This order cannot be cancelled.'}
            }, status=status.HTTP_400_BAD_REQUEST)

        reason = request.data.get('reason', '')
        order.cancel(reason)
        OrderStatusHistory.log_status_change(order, 'cancelled', reason, request.user)

        return Response({
            'success': True,
            'message': 'Order cancelled.',
            'order': OrderDetailSerializer(order).data,
        })

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def confirm(self, request, pk=None):
        order = self.get_object()
        order.confirm()
        OrderStatusHistory.log_status_change(order, 'confirmed', 'Order confirmed', request.user)
        return Response({'success': True, 'message': 'Order confirmed.'})

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def ship(self, request, pk=None):
        order = self.get_object()
        serializer = ShipmentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        shipment = Shipment.objects.create(
            order=order,
            tracking_number=serializer.validated_data.get('tracking_number', ''),
            carrier=serializer.validated_data['carrier'],
            carrier_service=serializer.validated_data.get('carrier_service', ''),
            estimated_delivery=serializer.validated_data.get('estimated_delivery'),
            weight=serializer.validated_data.get('weight'),
            shipping_cost=serializer.validated_data.get('shipping_cost', 0),
            notes=serializer.validated_data.get('notes', ''),
        )

        if not shipment.tracking_number:
            from apps.common.utils import generate_tracking_number
            shipment.tracking_number = generate_tracking_number()
            shipment.save(update_fields=['tracking_number'])

        order.ship(shipment.tracking_number, shipment.carrier)
        OrderStatusHistory.log_status_change(order, 'shipped', f'Shipped via {shipment.carrier}', request.user)

        return Response({
            'success': True,
            'message': 'Order shipped.',
            'shipment': ShipmentSerializer(shipment).data,
        })

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def deliver(self, request, pk=None):
        order = self.get_object()
        order.deliver()
        OrderStatusHistory.log_status_change(order, 'delivered', 'Order delivered', request.user)
        order_completed.send(sender=Order, order=order)
        return Response({'success': True, 'message': 'Order marked as delivered.'})

    @action(detail=True, methods=['get'])
    def tracking(self, request, pk=None):
        order = self.get_object()
        shipments = order.shipments.all()
        serializer = ShipmentSerializer(shipments, many=True)
        return Response({'success': True, 'shipments': serializer.data})

    @action(detail=True, methods=['get'])
    def status_history(self, request, pk=None):
        order = self.get_object()
        history = order.status_history.all()
        serializer = OrderStatusHistorySerializer(history, many=True)
        return Response({'success': True, 'history': serializer.data})

    @action(detail=True, methods=['post'])
    def add_note(self, request, pk=None):
        order = self.get_object()
        note_text = request.data.get('note', '')
        is_customer_visible = request.data.get('is_customer_visible', False)
        OrderNote.objects.create(
            order=order,
            note=note_text,
            is_customer_visible=is_customer_visible,
            created_by=request.user,
        )
        return Response({'success': True, 'message': 'Note added.'})

    @action(detail=True, methods=['get'])
    def notes(self, request, pk=None):
        order = self.get_object()
        if request.user.is_staff:
            notes = order.notes.all()
        else:
            notes = order.notes.filter(is_customer_visible=True)
        serializer = OrderNoteSerializer(notes, many=True)
        return Response({'success': True, 'notes': serializer.data})


class ReturnRequestViewSet(viewsets.ModelViewSet):
    serializer_class = ReturnRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return ReturnRequest.objects.all()
        return ReturnRequest.objects.filter(order__user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return ReturnRequestCreateSerializer
        return ReturnRequestSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from .models import OrderItem
        order_item = OrderItem.objects.get(
            pk=serializer.validated_data['order_item_id'],
            order__user=request.user
        )
        return_request = ReturnRequest.objects.create(
            order=order_item.order,
            order_item=order_item,
            reason=serializer.validated_data['reason'],
            quantity=serializer.validated_data['quantity'],
            refund_amount=order_item.unit_price * serializer.validated_data['quantity'],
        )
        return Response({
            'success': True,
            'message': 'Return request submitted.',
            'return_request': ReturnRequestSerializer(return_request).data,
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        return_request = self.get_object()
        return_request.approve(processed_by=request.user)
        return Response({'success': True, 'message': 'Return request approved.'})

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def reject(self, request, pk=None):
        return_request = self.get_object()
        notes = request.data.get('notes', '')
        return_request.reject(notes=notes, processed_by=request.user)
        return Response({'success': True, 'message': 'Return request rejected.'})


class AdminOrderStatsView(generics.GenericAPIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        from django.db.models import Sum, Count, Avg
        qs = Order.objects.all()
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        if date_from:
            qs = qs.filter(created_at__date__gte=date_from)
        if date_to:
            qs = qs.filter(created_at__date__lte=date_to)

        stats = {
            'total_orders': qs.count(),
            'pending_orders': qs.filter(status='pending').count(),
            'processing_orders': qs.filter(status='processing').count(),
            'shipped_orders': qs.filter(status='shipped').count(),
            'delivered_orders': qs.filter(status='delivered').count(),
            'cancelled_orders': qs.filter(status='cancelled').count(),
            'total_revenue': qs.filter(payment_status='paid').aggregate(
                total=Sum('total')
            )['total'] or 0,
            'average_order_value': qs.filter(payment_status='paid').aggregate(
                avg=Avg('total')
            )['avg'] or 0,
        }
        return Response({'success': True, 'stats': stats})
