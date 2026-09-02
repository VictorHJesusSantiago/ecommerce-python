from django.contrib import admin
from django.utils.html import format_html
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from mptt.admin import DraggableMPTTAdmin, TreeRelatedFieldListFilter
from .models import (
    Category, Brand, ProductCollection, Product, ProductVariant,
    ProductImage, ProductAttribute, ProductAttributeValue,
    VariantAttributeValue, ProductRecommendation
)


class ProductResource(resources.ModelResource):
    class Meta:
        model = Product
        skip_unchanged = True
        use_bulk = True


@admin.register(Category)
class CategoryAdmin(DraggableMPTTAdmin):
    list_display = ['tree_actions', 'indented_title', 'slug', 'is_active', 'product_count', 'sort_order']
    list_filter = ['is_active', 'show_in_menu']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'product_count', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(ProductCollection)
class ProductCollectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'sort_order']
    list_filter = ['is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['products']


@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    resource_class = ProductResource
    list_display = ['name', 'sku', 'category', 'brand', 'price', 'quantity', 'status', 'is_active', 'is_featured', 'rating_avg', 'created_at']
    list_filter = ['status', 'is_active', 'is_featured', 'is_digital', 'category', 'brand', 'product_type']
    search_fields = ['name', 'sku', 'barcode', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['views_count', 'sold_count', 'rating_avg', 'rating_count', 'created_at', 'updated_at']
    list_editable = ['price', 'quantity', 'status', 'is_active', 'is_featured']
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'slug', 'sku', 'barcode', 'description', 'short_description', 'status')
        }),
        ('Classification', {
            'fields': ('category', 'brand', 'vendor', 'product_type', 'tags')
        }),
        ('Pricing', {
            'fields': ('price', 'compare_at_price', 'cost_price', 'is_taxable', 'tax_class')
        }),
        ('Inventory', {
            'fields': ('track_inventory', 'quantity', 'low_stock_threshold', 'allow_backorder')
        }),
        ('Shipping', {
            'fields': ('weight', 'length', 'width', 'height')
        }),
        ('Display', {
            'fields': ('is_active', 'is_featured', 'is_digital', 'sort_order')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description')
        }),
        ('Stats', {
            'fields': ('views_count', 'sold_count', 'rating_avg', 'rating_count')
        }),
        ('Relationships', {
            'fields': ('related_products', 'up_sells', 'cross_sells')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['name', 'product', 'sku', 'price', 'quantity', 'is_active']
    list_filter = ['is_active', 'product']
    search_fields = ['name', 'sku', 'product__name']
    list_editable = ['price', 'quantity', 'is_active']


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'alt_text', 'is_primary', 'sort_order']
    list_filter = ['is_primary', 'product']
    search_fields = ['product__name', 'alt_text']
    list_editable = ['is_primary', 'sort_order']


@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'type', 'is_required', 'is_filterable', 'is_variant', 'sort_order']
    list_filter = ['type', 'is_required', 'is_filterable', 'is_variant']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(ProductAttributeValue)
class ProductAttributeValueAdmin(admin.ModelAdmin):
    list_display = ['product', 'attribute', 'value']
    search_fields = ['product__name', 'attribute__name', 'value']


@admin.register(VariantAttributeValue)
class VariantAttributeValueAdmin(admin.ModelAdmin):
    list_display = ['variant', 'attribute', 'value']
    search_fields = ['variant__name', 'attribute__name', 'value']


@admin.register(ProductRecommendation)
class ProductRecommendationAdmin(admin.ModelAdmin):
    list_display = ['product', 'recommended', 'ranking', 'recommendation_type']
    list_filter = ['recommendation_type']
    search_fields = ['product__name', 'recommended__name']
