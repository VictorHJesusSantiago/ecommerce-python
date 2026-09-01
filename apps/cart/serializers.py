from rest_framework import serializers
from .models import Cart, CartItem, SavedItem
from apps.products.serializers import ProductListSerializer, ProductVariantSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product_detail = ProductListSerializer(source='product', read_only=True)
    variant_detail = ProductVariantSerializer(source='variant', read_only=True)
    unit_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    line_total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    is_available = serializers.BooleanField(read_only=True)

    class Meta:
        model = CartItem
        fields = [
            'id', 'product', 'product_detail', 'variant', 'variant_detail',
            'quantity', 'unit_price', 'line_total', 'is_available', 'notes',
            'created_at',
        ]
        read_only_fields = ['id', 'unit_price', 'line_total', 'is_available', 'created_at']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    discount_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    total_items_count = serializers.IntegerField(read_only=True)
    coupon_code = serializers.CharField(source='coupon.code', read_only=True, default=None)

    class Meta:
        model = Cart
        fields = [
            'id', 'user', 'session_key', 'is_active', 'coupon', 'coupon_code',
            'notes', 'currency', 'items', 'subtotal', 'discount_amount',
            'total', 'total_items', 'total_items_count', 'created_at',
        ]
        read_only_fields = ['id', 'user', 'subtotal', 'discount_amount', 'total', 'created_at']


class CartAddItemSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()
    variant_id = serializers.UUIDField(required=False, allow_null=True)
    quantity = serializers.IntegerField(min_value=1, max_value=99, default=1)


class CartUpdateItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=0, max_value=99)


class CartApplyCouponSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=50)


class SavedItemSerializer(serializers.ModelSerializer):
    product_detail = ProductListSerializer(source='product', read_only=True)

    class Meta:
        model = SavedItem
        fields = ['id', 'product', 'product_detail', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']
