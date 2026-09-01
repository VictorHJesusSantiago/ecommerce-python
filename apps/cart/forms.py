from django import forms
from .models import Cart, CartItem


class CartForm(forms.ModelForm):
    class Meta:
        model = Cart
        fields = ['notes', 'currency']


class CartItemForm(forms.ModelForm):
    class Meta:
        model = CartItem
        fields = ['product', 'variant', 'quantity']
        widgets = {
            'quantity': forms.NumberInput(attrs={'min': 1, 'max': 99}),
        }

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity < 1:
            raise forms.ValidationError('Quantity must be at least 1.')
        if quantity > 99:
            raise forms.ValidationError('Maximum quantity is 99.')
        return quantity


class CouponApplyForm(forms.Form):
    code = forms.CharField(max_length=50, widget=forms.TextInput(attrs={
        'placeholder': 'Enter coupon code'
    }))
