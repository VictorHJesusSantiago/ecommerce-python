from django import forms
from .models import Warehouse, StockItem, StockTransfer, Supplier, PurchaseOrder


class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ['name', 'code', 'address_line1', 'address_line2', 'city', 'state',
                  'postal_code', 'country', 'phone', 'email', 'manager', 'priority',
                  'shipping_cost_per_kg', 'is_active']


class StockItemForm(forms.ModelForm):
    class Meta:
        model = StockItem
        fields = ['product', 'variant', 'warehouse', 'quantity', 'reserved_quantity',
                  'low_stock_threshold', 'reorder_point', 'reorder_quantity', 'cost_price', 'location']


class StockAdjustForm(forms.Form):
    stock_item = forms.ModelChoiceField(queryset=StockItem.objects.all())
    quantity_change = forms.IntegerField()
    reason = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'code', 'contact_name', 'email', 'phone', 'address',
                  'website', 'payment_terms', 'lead_time_days', 'is_active', 'notes']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
