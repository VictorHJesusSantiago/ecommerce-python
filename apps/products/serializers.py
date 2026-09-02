from rest_framework import serializers
from .models import (
    Category, Brand, ProductCollection, Product, ProductVariant,
    ProductImage, ProductAttribute, ProductAttributeValue,
    VariantAttributeValue, ProductRecommendation
)
from django.db.models import Avg


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    product_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description', 'parent', 'image', 'icon',
            'is_active', 'sort_order', 'show_in_menu', 'product_count',
            'children', 'meta_title', 'meta_description', 'created_at',
        ]
        read_only_fields = ['id', 'slug', 'product_count', 'created_at']

    def get_children(self, obj):
        children = obj.get_children().filter(is_active=True)
        return CategoryListSerializer(children, many=True).data


class CategoryListSerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField(read_only=True)
    children_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'image', 'icon', 'product_count', 'children_count']


class CategoryTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'children', 'product_count', 'level']

    def get_children(self, obj):
        children = obj.get_children().filter(is_active=True)
        return CategoryTreeSerializer(children, many=True).data


class BrandSerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Brand
        fields = ['id', 'name', 'slug', 'description', 'logo', 'website', 'is_active', 'product_count', 'created_at']
        read_only_fields = ['id', 'slug', 'product_count', 'created_at']


class ProductCollectionSerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = ProductCollection
        fields = ['id', 'name', 'slug', 'description', 'image', 'is_active', 'product_count', 'created_at']
        read_only_fields = ['id', 'slug', 'created_at']

    def get_product_count(self, obj):
        return obj.products.filter(is_active=True).count()


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'title', 'is_primary', 'sort_order']
        read_only_fields = ['id']


class ProductAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAttribute
        fields = ['id', 'name', 'slug', 'type', 'is_required', 'is_filterable', 'is_variant', 'sort_order']
        read_only_fields = ['id', 'slug']


class ProductAttributeValueSerializer(serializers.ModelSerializer):
    attribute_name = serializers.CharField(source='attribute.name', read_only=True)

    class Meta:
        model = ProductAttributeValue
        fields = ['id', 'attribute', 'attribute_name', 'value']


class VariantAttributeValueSerializer(serializers.ModelSerializer):
    attribute_name = serializers.CharField(source='attribute.name', read_only=True)

    class Meta:
        model = VariantAttributeValue
        fields = ['id', 'attribute', 'attribute_name', 'value']


class ProductVariantSerializer(serializers.ModelSerializer):
    attribute_values = VariantAttributeValueSerializer(many=True, read_only=True)
    is_in_stock = serializers.BooleanField(read_only=True)
    is_on_sale = serializers.BooleanField(read_only=True)

    class Meta:
        model = ProductVariant
        fields = [
            'id', 'name', 'sku', 'price', 'compare_at_price', 'quantity',
            'low_stock_threshold', 'weight', 'barcode', 'image', 'sort_order',
            'options', 'is_active', 'is_in_stock', 'is_on_sale',
            'attribute_values', 'created_at',
        ]
        read_only_fields = ['id', 'sku', 'is_in_stock', 'is_on_sale', 'created_at']


class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    primary_image = serializers.SerializerMethodField()
    is_in_stock = serializers.BooleanField(read_only=True)
    is_on_sale = serializers.BooleanField(read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    lowest_variant_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'sku', 'category', 'category_name',
            'brand', 'brand_name', 'product_type', 'price', 'compare_at_price',
            'is_active', 'is_featured', 'status', 'rating_avg', 'rating_count',
            'views_count', 'sold_count', 'primary_image', 'is_in_stock',
            'is_on_sale', 'discount_percentage', 'lowest_variant_price',
            'created_at',
        ]

    def get_primary_image(self, obj):
        image = obj.images.filter(is_primary=True).first()
        if image:
            return ProductImageSerializer(image).data
        image = obj.images.first()
        if image:
            return ProductImageSerializer(image).data
        return None


class ProductDetailSerializer(serializers.ModelSerializer):
    category_detail = CategoryListSerializer(source='category', read_only=True)
    brand_detail = BrandSerializer(source='brand', read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    attribute_values = ProductAttributeValueSerializer(many=True, read_only=True)
    is_in_stock = serializers.BooleanField(read_only=True)
    is_on_sale = serializers.BooleanField(read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    tags = serializers.StringRelatedField(many=True, read_only=True)
    related_products_summary = serializers.SerializerMethodField()
    review_summary = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'sku', 'barcode', 'description',
            'short_description', 'category', 'category_detail', 'brand',
            'brand_detail', 'vendor', 'product_type', 'price',
            'compare_at_price', 'cost_price', 'track_inventory', 'quantity',
            'low_stock_threshold', 'allow_backorder', 'weight', 'length',
            'width', 'height', 'is_active', 'is_featured', 'is_digital',
            'is_taxable', 'tax_class', 'status', 'views_count', 'sold_count',
            'rating_avg', 'rating_count', 'is_in_stock', 'is_on_sale',
            'discount_percentage', 'tags', 'variants', 'images',
            'attribute_values', 'related_products_summary', 'review_summary',
            'meta_title', 'meta_description', 'sort_order', 'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'slug', 'sku', 'views_count', 'sold_count',
            'rating_avg', 'rating_count', 'created_at', 'updated_at',
        ]

    def get_related_products_summary(self, obj):
        related = obj.related_products.filter(is_active=True)[:6]
        return ProductListSerializer(related, many=True).data

    def get_review_summary(self, obj):
        reviews = obj.reviews.filter(is_approved=True)
        if not reviews.exists():
            return {'average': 0, 'count': 0, 'distribution': {}}
        avg = reviews.aggregate(avg=Avg('rating'))['avg']
        distribution = {}
        for i in range(1, 6):
            distribution[str(i)] = reviews.filter(rating=i).count()
        return {
            'average': round(float(avg), 2) if avg else 0,
            'count': reviews.count(),
            'distribution': distribution,
        }


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, required=False)
    attribute_values = ProductAttributeValueSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = [
            'name', 'slug', 'sku', 'barcode', 'description', 'short_description',
            'category', 'brand', 'product_type', 'price', 'compare_at_price',
            'cost_price', 'track_inventory', 'quantity', 'low_stock_threshold',
            'allow_backorder', 'weight', 'length', 'width', 'height',
            'is_active', 'is_featured', 'is_digital', 'is_taxable', 'tax_class',
            'status', 'meta_title', 'meta_description', 'sort_order',
            'images', 'attribute_values',
        ]

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        attributes_data = validated_data.pop('attribute_values', [])
        product = Product.objects.create(**validated_data)
        for image_data in images_data:
            ProductImage.objects.create(product=product, **image_data)
        for attr_data in attributes_data:
            ProductAttributeValue.objects.create(product=product, **attr_data)
        return product

    def update(self, instance, validated_data):
        images_data = validated_data.pop('images', None)
        attributes_data = validated_data.pop('attribute_values', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if images_data is not None:
            instance.images.all().delete()
            for image_data in images_data:
                ProductImage.objects.create(product=instance, **image_data)
        if attributes_data is not None:
            instance.attribute_values.all().delete()
            for attr_data in attributes_data:
                ProductAttributeValue.objects.create(product=instance, **attr_data)
        return instance


class ProductRecommendationSerializer(serializers.ModelSerializer):
    recommended_product = ProductListSerializer(source='recommended', read_only=True)

    class Meta:
        model = ProductRecommendation
        fields = ['id', 'recommended', 'recommended_product', 'ranking', 'recommendation_type']
