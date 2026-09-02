from django.contrib import admin
from .models import Review, ReviewImage, ReviewVote, ReviewReport, ReviewSummary


class ReviewImageInline(admin.TabularInline):
    model = ReviewImage
    extra = 0
    readonly_fields = ['image', 'alt_text']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'rating', 'title', 'is_verified_purchase', 'is_approved', 'helpful_count', 'created_at']
    list_filter = ['rating', 'is_verified_purchase', 'is_approved']
    search_fields = ['user__email', 'product__name', 'title', 'body']
    raw_id_fields = ['user', 'product', 'order_item']
    inlines = [ReviewImageInline]
    actions = ['approve_reviews']

    def approve_reviews(self, request, queryset):
        for review in queryset.filter(is_approved=False):
            review.approve()
        self.message_user(request, f"Approved {queryset.count()} reviews.")
    approve_reviews.short_description = "Approve selected reviews"


@admin.register(ReviewImage)
class ReviewImageAdmin(admin.ModelAdmin):
    list_display = ['review', 'alt_text', 'sort_order']
    raw_id_fields = ['review']


@admin.register(ReviewVote)
class ReviewVoteAdmin(admin.ModelAdmin):
    list_display = ['review', 'user', 'vote_type', 'created_at']
    search_fields = ['user__email']
    raw_id_fields = ['review', 'user']


@admin.register(ReviewReport)
class ReviewReportAdmin(admin.ModelAdmin):
    list_display = ['review', 'user', 'reason', 'is_resolved', 'created_at']
    list_filter = ['reason', 'is_resolved']
    search_fields = ['user__email']
    raw_id_fields = ['review', 'user']
    readonly_fields = ['resolved_at', 'created_at']


@admin.register(ReviewSummary)
class ReviewSummaryAdmin(admin.ModelAdmin):
    list_display = ['product', 'total_reviews', 'avg_rating', 'verified_count']
    search_fields = ['product__name']
    raw_id_fields = ['product']
