from rest_framework import viewsets, status, permissions, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, F
from django.core.cache import cache

from .models import SearchQuery, PopularSearch, SearchSuggestion, SavedSearch
from .serializers import (
    SearchQuerySerializer, PopularSearchSerializer, SearchSuggestionSerializer,
    SavedSearchSerializer, SearchRequestSerializer, SearchResultsSerializer
)
from apps.common.pagination import SearchPagination


class SearchView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    pagination_class = SearchPagination

    def get(self, request):
        serializer = SearchRequestSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        query = serializer.validated_data['q']
        from apps.products.models import Product
        from django.db.models import Q

        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(sku__icontains=query) |
            Q(brand__name__icontains=query) |
            Q(tags__name__icontains=query),
            is_active=True,
            status='active'
        ).distinct()

        category = serializer.validated_data.get('category')
        if category:
            products = products.filter(category_id=category)

        brand = serializer.validated_data.get('brand')
        if brand:
            products = products.filter(brand_id=brand)

        min_price = serializer.validated_data.get('min_price')
        if min_price:
            products = products.filter(price__gte=min_price)

        max_price = serializer.validated_data.get('max_price')
        if max_price:
            products = products.filter(price__lte=max_price)

        rating = serializer.validated_data.get('rating')
        if rating:
            products = products.filter(rating_avg__gte=rating)

        in_stock = serializer.validated_data.get('in_stock')
        if in_stock:
            products = products.filter(Q(quantity__gt=0) | Q(allow_backorder=True))

        sort_by = serializer.validated_data.get('sort_by', 'relevance')
        if sort_by == 'price_asc':
            products = products.order_by('price')
        elif sort_by == 'price_desc':
            products = products.order_by('-price')
        elif sort_by == 'rating':
            products = products.order_by('-rating_avg')
        elif sort_by == 'newest':
            products = products.order_by('-created_at')
        elif sort_by == 'popular':
            products = products.order_by('-sold_count')

        page = serializer.validated_data.get('page', 1)
        page_size = serializer.validated_data.get('page_size', 20)
        from django.core.paginator import Paginator, EmptyPage
        paginator = Paginator(products, page_size)
        try:
            items = paginator.page(page)
        except EmptyPage:
            items = paginator.page(paginator.num_pages)

        from apps.products.serializers import ProductListSerializer
        from apps.common.signals import search_performed

        SearchQuery.objects.create(
            user=request.user if request.user.is_authenticated else None,
            query=query,
            results_count=paginator.count,
            ip_address=request.META.get('REMOTE_ADDR'),
        )
        PopularSearch.record_search(query)

        suggestions = self._get_suggestions(query)

        return Response({
            'success': True,
            'results': {
                'products': ProductListSerializer(items.object_list, many=True).data,
                'total_count': paginator.count,
                'page': items.number,
                'pages': paginator.num_pages,
                'suggestions': suggestions,
                'filters_applied': {
                    'query': query,
                    'category': category,
                    'brand': brand,
                    'min_price': str(min_price) if min_price else None,
                    'max_price': str(max_price) if max_price else None,
                }
            }
        })

    def _get_suggestions(self, query):
        cache_key = f"search_suggestions:{query}"
        suggestions = cache.get(cache_key)
        if suggestions is None:
            suggestions = list(
                SearchSuggestion.objects.filter(
                    query__icontains=query, is_active=True
                ).values_list('suggestion', flat=True)[:5]
            )
            if not suggestions:
                suggestions = list(
                    PopularSearch.objects.filter(
                        query__icontains=query
                    ).values_list('query', flat=True)[:5]
                )
            cache.set(cache_key, suggestions, 300)
        return suggestions


class AutocompleteView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        query = request.query_params.get('q', '').strip()
        if len(query) < 2:
            return Response({'success': True, 'suggestions': []})

        suggestions = cache.get(f"autocomplete:{query}")
        if suggestions is None:
            from apps.products.models import Product
            product_suggestions = Product.objects.filter(
                Q(name__icontains=query),
                is_active=True
            ).values_list('name', flat=True)[:5]

            category_suggestions = []
            from apps.products.models import Category
            category_suggestions = list(
                Category.objects.filter(name__icontains=query, is_active=True)
                .values_list('name', flat=True)[:3]
            )

            popular = PopularSearch.objects.filter(
                query__icontains=query
            ).values_list('query', flat=True)[:3]

            suggestions = {
                'products': list(product_suggestions),
                'categories': category_suggestions,
                'popular': list(popular),
            }
            cache.set(f"autocomplete:{query}", suggestions, 120)

        return Response({'success': True, 'suggestions': suggestions})


class PopularSearchViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PopularSearchSerializer
    queryset = PopularSearch.objects.all()[:20]


class SavedSearchViewSet(viewsets.ModelViewSet):
    serializer_class = SavedSearchSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SavedSearch.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
