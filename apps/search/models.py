from django.db import models
from apps.common.models import TimeStampedModel, UUIDModel


class SearchQuery(UUIDModel, TimeStampedModel):
    user = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='search_queries'
    )
    query = models.CharField(max_length=500, db_index=True)
    results_count = models.PositiveIntegerField(default=0)
    filters_used = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    session_key = models.CharField(max_length=255, blank=True, default='')
    clicked_product = models.ForeignKey(
        'products.Product', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='search_clicks'
    )

    class Meta:
        verbose_name = 'Search Query'
        verbose_name_plural = 'Search Queries'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['query']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.query


class PopularSearch(UUIDModel, TimeStampedModel):
    query = models.CharField(max_length=500, unique=True)
    count = models.PositiveIntegerField(default=0)
    last_searched = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Popular Search'
        verbose_name_plural = 'Popular Searches'
        ordering = ['-count']

    def __str__(self):
        return f"{self.query} ({self.count})"

    @classmethod
    def record_search(cls, query_text):
        obj, created = cls.objects.get_or_create(
            query=query_text.lower().strip(),
            defaults={'count': 1}
        )
        if not created:
            obj.count += 1
            obj.save(update_fields=['count', 'last_searched'])


class SearchSuggestion(UUIDModel):
    query = models.CharField(max_length=500, db_index=True)
    suggestion = models.CharField(max_length=500)
    score = models.FloatField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Search Suggestion'
        verbose_name_plural = 'Search Suggestions'
        ordering = ['-score']

    def __str__(self):
        return f"{self.query} -> {self.suggestion}"


class SavedSearch(UUIDModel, TimeStampedModel):
    user = models.ForeignKey(
        'users.User', on_delete=models.CASCADE,
        related_name='saved_searches'
    )
    name = models.CharField(max_length=200)
    query = models.CharField(max_length=500)
    filters = models.JSONField(default=dict, blank=True)
    notify_new_results = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Saved Search'
        verbose_name_plural = 'Saved Searches'
        ordering = ['-created_at']
        unique_together = ['user', 'name']

    def __str__(self):
        return f"{self.name}: {self.query}"
