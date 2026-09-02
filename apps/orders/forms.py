from django import forms
from .models import Order, OrderNote, ReturnRequest


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'status', 'payment_status', 'shipping_amount', 'tax_amount',
            'admin_notes', 'tracking_number', 'shipping_carrier',
        ]


class OrderNoteForm(forms.ModelForm):
    class Meta:
        model = OrderNote
        fields = ['note', 'is_customer_visible']
        widgets = {
            'note': forms.Textarea(attrs={'rows': 3}),
        }


class OrderSearchForm(forms.Form):
    order_number = forms.CharField(required=False)
    status = forms.ChoiceField(
        choices=[('', 'All')] + Order.STATUS_CHOICES,
        required=False
    )
    payment_status = forms.ChoiceField(
        choices=[('', 'All')] + Order.PAYMENT_STATUS_CHOICES,
        required=False
    )
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    search = forms.CharField(required=False)


class ReturnRequestForm(forms.ModelForm):
    class Meta:
        model = ReturnRequest
        fields = ['reason', 'quantity']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 4}),
        }
