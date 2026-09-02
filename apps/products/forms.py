from django import forms
from .models import Category, Brand, Product, ProductVariant, ProductAttribute


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'parent', 'slug', 'image', 'icon',
                  'is_active', 'sort_order', 'show_in_menu', 'meta_title', 'meta_description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'meta_description': forms.Textarea(attrs={'rows': 3}),
        }


class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['name', 'slug', 'description', 'logo', 'website', 'is_active']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'slug', 'sku', 'barcode', 'description', 'short_description',
            'category', 'brand', 'product_type', 'price', 'compare_at_price',
            'cost_price', 'track_inventory', 'quantity', 'low_stock_threshold',
            'allow_backorder', 'weight', 'length', 'width', 'height',
            'is_active', 'is_featured', 'is_digital', 'is_taxable', 'tax_class',
            'status', 'meta_title', 'meta_description', 'sort_order',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6}),
            'short_description': forms.Textarea(attrs={'rows': 3}),
            'meta_description': forms.Textarea(attrs={'rows': 3}),
            'price': forms.NumberInput(attrs={'step': '0.01'}),
            'compare_at_price': forms.NumberInput(attrs={'step': '0.01'}),
            'cost_price': forms.NumberInput(attrs={'step': '0.01'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        price = cleaned_data.get('price')
        compare_at_price = cleaned_data.get('compare_at_price')
        if compare_at_price and price and compare_at_price <= price:
            self.add_error('compare_at_price', 'Compare at price must be greater than price.')
        return cleaned_data


class ProductVariantForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = ['name', 'sku', 'price', 'compare_at_price', 'quantity',
                  'low_stock_threshold', 'weight', 'barcode', 'image',
                  'sort_order', 'options', 'is_active']
        widgets = {
            'options': forms.Textarea(attrs={'rows': 3}),
        }


class ProductSearchForm(forms.Form):
    q = forms.CharField(required=False, label='Search')
    category = forms.ModelChoiceField(queryset=Category.objects.filter(is_active=True), required=False)
    brand = forms.ModelChoiceField(queryset=Brand.objects.filter(is_active=True), required=False)
    min_price = forms.DecimalField(required=False, min_value=0)
    max_price = forms.DecimalField(required=False, min_value=0)
    in_stock = forms.BooleanField(required=False)
    on_sale = forms.BooleanField(required=False)
    sort_by = forms.ChoiceField(
        choices=[
            ('', 'Relevance'),
            ('price', 'Price: Low to High'),
            ('-price', 'Price: High to Low'),
            ('-created_at', 'Newest'),
            ('-rating_avg', 'Top Rated'),
            ('-sold_count', 'Best Selling'),
        ],
        required=False
    )


class ProductAttributeForm(forms.ModelForm):
    class Meta:
        model = ProductAttribute
        fields = ['name', 'slug', 'type', 'is_required', 'is_filterable', 'is_variant', 'sort_order']
