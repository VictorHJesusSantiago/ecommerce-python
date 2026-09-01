from django.contrib import admin
from django.utils.html import format_html
from import_export import resources
from import_export.admin import ImportExportModelAdmin


class TimeStampedAdmin(admin.ModelAdmin):
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 25


class SoftDeleteAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return self.model.all_objects.all()

    def soft_delete_selected(self, request, queryset):
        count = queryset.count()
        for obj in queryset:
            obj.soft_delete()
        self.message_user(request, f"Successfully soft-deleted {count} items.")

    soft_delete_selected.short_description = "Soft delete selected items"

    actions = ['soft_delete_selected']


class ExportMixin:
    def get_export_formats(self):
        return ('csv', 'xlsx')


class BaseResource(resources.ModelResource):
    class Meta:
        skip_unchanged = True
        report_skipped = True
        use_bulk = True
        batch_size = 1000
