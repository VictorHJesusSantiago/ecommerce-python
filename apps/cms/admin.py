from django.contrib import admin
from .models import Page, MenuItem, Menu, FAQ, Testimonial, Partner, ContactMessage, Subscriber


class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 0
    fields = ['title', 'url', 'page', 'target', 'sort_order', 'is_active']


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'is_published', 'published_at', 'sort_order', 'show_in_menu', 'created_at']
    list_filter = ['is_published', 'show_in_menu', 'template']
    search_fields = ['title', 'slug', 'content']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [MenuItemInline]


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'menu', 'parent', 'sort_order', 'is_active']
    list_filter = ['menu', 'is_active']
    search_fields = ['title']


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'category', 'sort_order', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['question', 'answer']


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['customer_name', 'customer_title', 'rating', 'sort_order', 'is_active']
    list_filter = ['rating', 'is_active']
    search_fields = ['customer_name', 'content']


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ['name', 'website', 'sort_order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['created_at']


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'is_active', 'source', 'created_at']
    list_filter = ['is_active', 'source']
    search_fields = ['email', 'first_name']
