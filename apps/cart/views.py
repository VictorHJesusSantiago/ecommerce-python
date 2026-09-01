from rest_framework import viewsets, status, permissions, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Cart, CartItem, SavedItem
from .serializers import (
    CartSerializer, CartItemSerializer, CartAddItemSerializer,
    CartUpdateItemSerializer, CartApplyCouponSerializer, SavedItemSerializer
)
from apps.common.signals import cart_updated
from apps.common.exceptions import CartError, InsufficientStockError


class CartViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def _get_cart(self, request):
        if request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=request.user, is_active=True)
        else:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key
            cart, _ = Cart.objects.get_or_create(
                session_key=session_key, is_active=True
            )
        return cart

    def list(self, request):
        cart = self._get_cart(request)
        serializer = CartSerializer(cart)
        return Response({'success': True, 'cart': serializer.data})

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        cart = self._get_cart(request)
        serializer = CartAddItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from apps.products.models import Product, ProductVariant
        product = get_object_or_404(Product, pk=serializer.validated_data['product_id'], is_active=True)
        variant = None
        if serializer.validated_data.get('variant_id'):
            variant = get_object_or_404(
                ProductVariant, pk=serializer.validated_data['variant_id'],
                product=product, is_active=True
            )

        quantity = serializer.validated_data['quantity']
        if product.track_inventory:
            available = variant.quantity if variant else product.quantity
            existing_item = CartItem.objects.filter(
                cart=cart, product=product, variant=variant
            ).first()
            existing_qty = existing_item.quantity if existing_item else 0
            if available < (existing_qty + quantity) and not product.allow_backorder:
                raise InsufficientStockError(
                    detail=f'Only {available - existing_qty} more items available.'
                )

        item = cart.add_item(product, quantity, variant)
        CartHistory.log(cart, 'item_added', {
            'product_id': str(product.id),
            'quantity': quantity,
            'variant_id': str(variant.id) if variant else None,
        })
        cart_updated.send(sender=Cart, cart=cart, item=item)

        return Response({
            'success': True,
            'message': 'Item added to cart.',
            'cart': CartSerializer(cart).data,
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def update_item(self, request):
        cart = self._get_cart(request)
        item_id = request.data.get('item_id')
        serializer = CartUpdateItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        quantity = serializer.validated_data['quantity']
        item = cart.update_item_quantity(item_id, quantity)

        if quantity == 0:
            CartHistory.log(cart, 'item_removed', {'item_id': str(item_id)})
            return Response({'success': True, 'message': 'Item removed from cart.', 'cart': CartSerializer(cart).data})

        CartHistory.log(cart, 'item_updated', {
            'item_id': str(item_id),
            'quantity': quantity,
        })

        return Response({'success': True, 'message': 'Cart updated.', 'cart': CartSerializer(cart).data})

    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        cart = self._get_cart(request)
        item_id = request.data.get('item_id')
        if not item_id:
            return Response({'success': False, 'error': {'message': 'item_id is required.'}}, status=400)
        success = cart.remove_item(item_id)
        if success:
            CartHistory.log(cart, 'item_removed', {'item_id': str(item_id)})
            return Response({'success': True, 'message': 'Item removed.', 'cart': CartSerializer(cart).data})
        return Response({'success': False, 'error': {'message': 'Item not found.'}}, status=404)

    @action(detail=False, methods=['post'])
    def apply_coupon(self, request):
        cart = self._get_cart(request)
        serializer = CartApplyCouponSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from apps.marketing.models import Coupon
        code = serializer.validated_data['code']
        try:
            coupon = Coupon.objects.get(code__iexact=code, is_active=True)
        except Coupon.DoesNotExist:
            raise CartError(detail='Invalid coupon code.')

        if not coupon.is_valid():
            raise CartError(detail='This coupon has expired or is no longer valid.')

        cart.coupon = coupon
        cart.save(update_fields=['coupon', 'updated_at'])

        discount = coupon.calculate_discount(cart.subtotal)
        CartHistory.log(cart, 'coupon_applied', {
            'coupon_code': code,
            'discount': str(discount),
        })

        return Response({
            'success': True,
            'message': f'Coupon applied. Discount: ${discount}',
            'discount': str(discount),
            'cart': CartSerializer(cart).data,
        })

    @action(detail=False, methods=['post'])
    def remove_coupon(self, request):
        cart = self._get_cart(request)
        if cart.coupon:
            CartHistory.log(cart, 'coupon_removed', {'coupon_code': cart.coupon.code})
            cart.coupon = None
            cart.save(update_fields=['coupon', 'updated_at'])
        return Response({'success': True, 'message': 'Coupon removed.', 'cart': CartSerializer(cart).data})

    @action(detail=False, methods=['post'])
    def clear(self, request):
        cart = self._get_cart(request)
        CartHistory.log(cart, 'cart_cleared', {'items_count': cart.total_items_count})
        cart.clear()
        return Response({'success': True, 'message': 'Cart cleared.', 'cart': CartSerializer(cart).data})

    @action(detail=False, methods=['get'])
    def summary(self, request):
        cart = self._get_cart(request)
        return Response({
            'success': True,
            'total_items': cart.total_items,
            'total_items_count': cart.total_items_count,
            'subtotal': str(cart.subtotal),
            'discount_amount': str(cart.discount_amount),
            'total': str(cart.total),
            'coupon_code': cart.coupon.code if cart.coupon else None,
        })


class SavedItemViewSet(viewsets.ModelViewSet):
    serializer_class = SavedItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SavedItem.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
