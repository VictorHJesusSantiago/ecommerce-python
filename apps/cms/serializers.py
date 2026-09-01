from rest_framework import serializers
from .models import Page, MenuItem, Menu, FAQ, Testimonial, Partner, ContactMessage, Subscriber


class PageSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Page
        fields = [
            'id', 'title', 'slug', 'content', 'template', 'is_published',
            'published_at', 'featured_image', 'author', 'parent',
            'sort_order', 'show_in_menu', 'menu_label', 'meta_title',
            'meta_description', 'meta_keywords', 'children', 'created_at',
        ]
        read_only_fields = ['id', 'slug', 'created_at']

    def get_children(self, obj):
        children = obj.children.filter(is_active=True)
        return PageListSerializer(children, many=True).data


class PageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ['id', 'title', 'slug', 'is_published', 'published_at', 'sort_order', 'created_at']


class MenuItemSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    effective_url = serializers.CharField(read_only=True)

    class Meta:
        model = MenuItem
        fields = [
            'id', 'title', 'url', 'page', 'effective_url', 'target',
            'sort_order', 'is_active', 'css_class', 'children',
        ]

    def get_children(self, obj):
        children = obj.children.filter(is_active=True)
        return MenuItemSerializer(children, many=True).data


class MenuSerializer(serializers.ModelSerializer):
    items = MenuItemSerializer(many=True, read_only=True)

    class Meta:
        model = Menu
        fields = ['id', 'name', 'slug', 'is_active', 'items']


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ['id', 'question', 'answer', 'category', 'sort_order', 'is_active']


class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = [
            'id', 'customer_name', 'customer_title', 'customer_image',
            'content', 'rating', 'sort_order', 'is_active',
        ]


class PartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partner
        fields = ['id', 'name', 'logo', 'website', 'description', 'sort_order', 'is_active']


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = [
            'id', 'name', 'email', 'phone', 'subject', 'message',
            'status', 'replied_at', 'created_at',
        ]
        read_only_fields = ['id', 'status', 'replied_at', 'created_at']


class ContactMessageCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True, default='')
    subject = serializers.CharField(max_length=300)
    message = serializers.CharField()


class SubscriberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscriber
        fields = ['id', 'email', 'first_name', 'is_active', 'created_at']
        read_only_fields = ['id', 'is_active', 'created_at']
