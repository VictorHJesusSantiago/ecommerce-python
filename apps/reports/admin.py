from django.contrib import admin
from .models import Report, AnalyticsEvent, DailyStats, ProductPerformance, SalesForecast


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['name', 'report_type', 'status', 'date_from', 'date_to', 'generated_by', 'completed_at']
    list_filter = ['report_type', 'status']
    search_fields = ['name']
    readonly_fields = ['data', 'file', 'completed_at', 'error_message', 'created_at']


@admin.register(AnalyticsEvent)
class AnalyticsEventAdmin(admin.ModelAdmin):
    list_display = ['event_type', 'user', 'page_url', 'revenue', 'created_at']
    list_filter = ['event_type']
    search_fields = ['user__email', 'page_url']
    readonly_fields = ['created_at']


@admin.register(DailyStats)
class DailyStatsAdmin(admin.ModelAdmin):
    list_display = ['date', 'total_orders', 'total_revenue', 'new_customers', 'page_views', 'conversion_rate']
    readonly_fields = ['date']


@admin.register(ProductPerformance)
class ProductPerformanceAdmin(admin.ModelAdmin):
    list_display = ['product', 'date', 'views', 'add_to_carts', 'purchases', 'revenue']
    search_fields = ['product__name']
    raw_id_fields = ['product']


@admin.register(SalesForecast)
class SalesForecastAdmin(admin.ModelAdmin):
    list_display = ['date', 'predicted_revenue', 'predicted_orders', 'confidence', 'actual_revenue']
    readonly_fields = ['date']
