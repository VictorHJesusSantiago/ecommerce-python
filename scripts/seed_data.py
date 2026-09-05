#!/usr/bin/env python
"""Seed database with sample data."""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from decimal import Decimal
from django.contrib.auth import get_user_model
from apps.products.models import Category, Brand, Product, ProductImage
from apps.marketing.models import Coupon
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

print("Creating admin user...")
admin, _ = User.objects.get_or_create(
    email='admin@example.com',
    defaults={
        'username': 'admin',
        'is_staff': True,
        'is_superuser': True,
        'role': 'admin',
    }
)
admin.set_password('admin123')
admin.save()

print("Creating categories...")
categories_data = ['Electronics', 'Clothing', 'Home & Garden', 'Sports', 'Books', 'Beauty']
categories = {}
for name in categories_data:
    cat, _ = Category.objects.get_or_create(name=name, defaults={'slug': name.lower().replace(' ', '-')})
    categories[name] = cat

print("Creating brands...")
brands_data = ['Nike', 'Samsung', 'Apple', 'Sony', 'Adidas']
brands = {}
for name in brands_data:
    brand, _ = Brand.objects.get_or_create(name=name, defaults={'slug': name.lower()})
    brands[name] = brand

print("Creating products...")
products_data = [
    {'name': 'Wireless Headphones', 'price': Decimal('79.99'), 'category': 'Electronics', 'brand': 'Sony'},
    {'name': 'Running Shoes', 'price': Decimal('129.99'), 'category': 'Sports', 'brand': 'Nike'},
    {'name': 'Smart Watch', 'price': Decimal('249.99'), 'category': 'Electronics', 'brand': 'Apple'},
    {'name': 'T-Shirt', 'price': Decimal('29.99'), 'category': 'Clothing', 'brand': 'Adidas'},
    {'name': 'Smartphone', 'price': Decimal('999.99'), 'category': 'Electronics', 'brand': 'Samsung'},
]

for data in products_data:
    Product.objects.get_or_create(
        name=data['name'],
        defaults={
            'slug': data['name'].lower().replace(' ', '-'),
            'sku': f"SKU-{hash(data['name']) % 999999:06d}",
            'category': categories[data['category']],
            'brand': brands[data['brand']],
            'price': data['price'],
            'quantity': 100,
            'status': 'active',
            'is_active': True,
            'description': f"High quality {data['name']}",
            'short_description': f"Best {data['name']} in the market",
        }
    )

print("Creating coupons...")
now = timezone.now()
Coupon.objects.get_or_create(
    code='WELCOME10',
    defaults={
        'description': '10% off your first order',
        'discount_type': 'percentage',
        'discount_value': Decimal('10'),
        'start_date': now - timedelta(days=1),
        'end_date': now + timedelta(days=365),
        'is_active': True,
    }
)

Coupon.objects.get_or_create(
    code='SAVE20',
    defaults={
        'description': '$20 off orders over $100',
        'discount_type': 'fixed',
        'discount_value': Decimal('20'),
        'min_order_amount': Decimal('100'),
        'start_date': now - timedelta(days=1),
        'end_date': now + timedelta(days=365),
        'is_active': True,
    }
)

print("Seed data created successfully!")
