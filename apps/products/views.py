from rest_framework import viewsets, status, permissions, generics, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db.models import Q, Count, Avg
from django.core.cache import cache

from .models import (
    Category, Brand, ProductCollection, Product, ProductVariant,
    ProductImage, ProductAttribute, ProductAttributeValue,
    ProductRecommendation
)
from .serializers import (
    CategorySerializer, CategoryListSerializer, CategoryTreeSerializer,
    BrandSerializer, ProductCollectionSerializer, ProductListSerializer,
    ProductDetailSerializer, ProductCreateUpdateSerializer,
    ProductVariantSerializer, ProductImageSerializer,
    ProductAttributeSerializer, ProductRecommendationSerializer
)
from apps.common.permissions import IsAdminUser, CanManageProducts, ReadOnly
from apps.common.pagination import ProductPagination, StandardResultsSetPagination


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        qs = Category.objects.filter(is_active=True)
        parent = self.request.query_params.get('parent')
        if parent:
            qs = qs.filter(parent_id=parent)
        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return CategoryListSerializer
        if self.action == 'tree':
            return CategoryTreeSerializer
        return CategorySerializer

    @action(detail=False, methods=['get'])
    def tree(self, request):
        categories = Category.objects.filter(parent=None, is_active=True)
        serializer = CategoryTreeSerializer(categories, many=True)
        return Response({'success': True, 'categories': serializer.data})

    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        category = self.get_object()
        products = Product.objects.filter(
            category=category, is_active=True, status='active'
        )
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = ProductListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ProductListSerializer(products, many=True)
        return Response({'success': True, 'products': serializer.data})


class BrandViewSet(viewsets.ModelViewSet):
    serializer_class = BrandSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Brand.objects.filter(is_active=True)

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [IsAdminUser()]

    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        brand = self.get_object()
        products = Product.objects.filter(brand=brand, is_active=True, status='active')
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = ProductListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ProductListSerializer(products, many=True)
        return Response({'success': True, 'products': serializer.data})


class ProductCollectionViewSet(viewsets.ModelViewSet):
    serializer_class = ProductCollectionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return ProductCollection.objects.filter(is_active=True)


class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = ProductPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'brand', 'status', 'product_type', 'is_active', 'is_featured']
    search_fields = ['name', 'description', 'sku', 'barcode']
    ordering_fields = ['price', 'rating_avg', 'sold_count', 'views_count', 'created_at', 'name']
    ordering = ['-created_at']

    def get_queryset(self):
        qs = Product.objects.filter(status='active', is_active=True)
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            qs = qs.filter(price__gte=min_price)
        if max_price:
            qs = qs.filter(price__lte=max_price)
        in_stock = self.request.query_params.get('in_stock')
        if in_stock and in_stock.lower() == 'true':
            qs = qs.filter(Q(quantity__gt=0) | Q(allow_backorder=True))
        on_sale = self.request.query_params.get('on_sale')
        if on_sale and on_sale.lower() == 'true':
            qs = qs.filter(compare_at_price__isnull=False, compare_at_price__gt=models.F('price'))
        brand = self.request.query_params.get('brand')
        if brand:
            qs = qs.filter(brand_id=brand)
        tags = self.request.query_params.get('tags')
        if tags:
            qs = qs.filter(tags__name__in=tags.split(',')).distinct()
        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return ProductCreateUpdateSerializer
        return ProductDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.increment_views()
        serializer = self.get_serializer(instance)
        return Response({'success': True, 'product': serializer.data})

    @action(detail=False, methods=['get'])
    def featured(self, request):
        cache_key = 'featured_products'
        products = cache.get(cache_key)
        if products is None:
            products = Product.objects.filter(
                is_featured=True, is_active=True, status='active'
            )[:12]
            cache.set(cache_key, list(products), 600)
        serializer = ProductListSerializer(products, many=True)
        return Response({'success': True, 'products': serializer.data})

    @action(detail=False, methods=['get'])
    def new_arrivals(self, request):
        from django.utils import timezone
        from datetime import timedelta
        week_ago = timezone.now() - timedelta(days=7)
        products = Product.objects.filter(
            is_active=True, status='active', created_at__gte=week_ago
        ).order_by('-created_at')[:20]
        serializer = ProductListSerializer(products, many=True)
        return Response({'success': True, 'products': serializer.data})

    @action(detail=False, methods=['get'])
    def best_sellers(self, request):
        products = Product.objects.filter(
            is_active=True, status='active'
        ).order_by('-sold_count')[:20]
        serializer = ProductListSerializer(products, many=True)
        return Response({'success': True, 'products': serializer.data})

    @action(detail=False, methods=['get'])
    def top_rated(self, request):
        products = Product.objects.filter(
            is_active=True, status='active', rating_count__gte=1
        ).order_by('-rating_avg')[:20]
        serializer = ProductListSerializer(products, many=True)
        return Response({'success': True, 'products': serializer.data})

    @action(detail=True, methods=['get'])
    def recommendations(self, request, pk=None):
        product = self.get_object()
        recommendations = ProductRecommendation.objects.filter(
            product=product
        ).select_related('recommended')[:10]
        serializer = ProductRecommendationSerializer(recommendations, many=True)
        return Response({'success': True, 'recommendations': serializer.data})

    @action(detail=True, methods=['get'])
    def variants(self, request, pk=None):
        product = self.get_object()
        variants = product.variants.filter(is_active=True)
        serializer = ProductVariantSerializer(variants, many=True)
        return Response({'success': True, 'variants': serializer.data})

    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        from apps.reviews.models import Review
        product = self.get_object()
        reviews = Review.objects.filter(
            product=product, is_approved=True
        ).select_related('user')
        page = self.paginate_queryset(reviews)
        if page is not None:
            from apps.reviews.serializers import ReviewSerializer
            serializer = ReviewSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        from apps.reviews.serializers import ReviewSerializer
        serializer = ReviewSerializer(reviews, many=True)
        return Response({'success': True, 'reviews': serializer.data})


class ProductVariantViewSet(viewsets.ModelViewSet):
    serializer_class = ProductVariantSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        product_pk = self.kwargs.get('product_pk')
        if product_pk:
            return ProductVariant.objects.filter(product_id=product_pk)
        return ProductVariant.objects.all()

    def perform_create(self, serializer):
        product_pk = self.kwargs.get('product_pk')
        serializer.save(product_id=product_pk)


class ProductAttributeViewSet(viewsets.ModelViewSet):
    serializer_class = ProductAttributeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return ProductAttribute.objects.all()
