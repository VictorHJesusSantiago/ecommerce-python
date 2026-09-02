from django import forms
from .models import PaymentGateway, Transaction


class PaymentGatewayForm(forms.ModelForm):
    class Meta:
        model = PaymentGateway
        fields = ['name', 'code', 'is_active', 'config', 'supported_currencies',
                  'fee_percent', 'fee_fixed', 'test_mode']
        widgets = {
            'config': forms.Textarea(attrs={'rows': 5}),
            'supported_currencies': forms.Textarea(attrs={'rows': 2}),
        }


class TransactionSearchForm(forms.Form):
    transaction_id = forms.CharField(required=False)
    order_number = forms.CharField(required=False)
    status = forms.ChoiceField(
        choices=[('', 'All')] + Transaction.STATUS_CHOICES if hasattr(Transaction, 'STATUS_CHOICES') else [('', 'All')],
        required=False
    )
    gateway = forms.CharField(required=False)
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
