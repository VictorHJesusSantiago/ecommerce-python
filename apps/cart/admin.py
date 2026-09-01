from django.contrib import admin
from .models import Cart, CartItem, SavedItem, CartHistory


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['unit_price', 'line_total']
    fields = ['product', 'variant', 'quantity', 'unit_price', 'line_total']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'session_key', 'is_active', 'total_items', 'subtotal', 'created_at']
    list_filter = ['is_active', 'currency']
    search_fields = ['user__email', 'session_key']
    inlines = [CartItemInline]
    readonly_fields = ['subtotal', 'total_items', 'created_at', 'updated_at']

    def subtotal(self, obj):
        return obj.subtotal

    def total_items(self, obj):
        return obj.total_items


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'variant', 'quantity', 'unit_price', 'line_total']
    list_filter = ['cart__is_active']
    search_fields = ['product__name', 'cart__user__email']

    def unit_price(self, obj):
        return obj.unit_price

    def line_total(self, obj):
        return obj.line_total


@admin.register(SavedItem)
class SavedItemAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'created_at']
    search_fields = ['user__email', 'product__name']
    raw_id_fields = ['user', 'product']


@admin.register(CartHistory)
class CartHistoryAdmin(admin.ModelAdmin):
    list_display = ['cart', 'action', 'details', 'created_at']
    list_filter = ['action']
    search_fields = ['cart__user__email']
    readonly_fields = ['created_at']
