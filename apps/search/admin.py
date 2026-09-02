from django.contrib import admin
from .models import SearchQuery, PopularSearch, SearchSuggestion, SavedSearch


@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ['query', 'user', 'results_count', 'created_at']
    search_fields = ['query', 'user__email']
    readonly_fields = ['created_at']


@admin.register(PopularSearch)
class PopularSearchAdmin(admin.ModelAdmin):
    list_display = ['query', 'count', 'last_searched']
    search_fields = ['query']


@admin.register(SearchSuggestion)
class SearchSuggestionAdmin(admin.ModelAdmin):
    list_display = ['query', 'suggestion', 'score', 'is_active']
    list_filter = ['is_active']
    search_fields = ['query', 'suggestion']


@admin.register(SavedSearch)
class SavedSearchAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'query', 'notify_new_results', 'created_at']
    search_fields = ['name', 'user__email', 'query']
    raw_id_fields = ['user']
