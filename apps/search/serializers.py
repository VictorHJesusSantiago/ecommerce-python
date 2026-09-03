from rest_framework import serializers
from .models import SearchQuery, PopularSearch, SearchSuggestion, SavedSearch
from apps.products.serializers import ProductListSerializer


class SearchQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchQuery
        fields = ['id', 'query', 'results_count', 'filters_used', 'created_at']
        read_only_fields = ['id', 'results_count', 'created_at']


class PopularSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = PopularSearch
        fields = ['id', 'query', 'count', 'last_searched']


class SearchSuggestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchSuggestion
        fields = ['id', 'query', 'suggestion', 'score']


class SavedSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedSearch
        fields = ['id', 'name', 'query', 'filters', 'notify_new_results', 'created_at']
        read_only_fields = ['id', 'created_at']


class SearchRequestSerializer(serializers.Serializer):
    q = serializers.CharField(max_length=500, required=True)
    category = serializers.UUIDField(required=False, allow_null=True)
    brand = serializers.UUIDField(required=False, allow_null=True)
    min_price = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
    max_price = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
    rating = serializers.IntegerField(required=False, allow_null=True, min_value=1, max_value=5)
    in_stock = serializers.BooleanField(required=False, allow_null=True)
    sort_by = serializers.ChoiceField(
        choices=[
            ('relevance', 'Relevance'),
            ('price_asc', 'Price: Low to High'),
            ('price_desc', 'Price: High to Low'),
            ('rating', 'Rating'),
            ('newest', 'Newest'),
            ('popular', 'Popular'),
        ],
        default='relevance',
        required=False
    )
    page = serializers.IntegerField(min_value=1, default=1, required=False)
    page_size = serializers.IntegerField(min_value=1, max_value=100, default=20, required=False)


class SearchResultsSerializer(serializers.Serializer):
    products = ProductListSerializer(many=True)
    total_count = serializers.IntegerField()
    page = serializers.IntegerField()
    pages = serializers.IntegerField()
    suggestions = serializers.ListField(child=serializers.CharField(), default=list)
    filters_applied = serializers.DictField(default=dict)
