from django import forms
from .models import Report


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['name', 'report_type', 'date_from', 'date_to', 'filters']
        widgets = {
            'date_from': forms.DateInput(attrs={'type': 'date'}),
            'date_to': forms.DateInput(attrs={'type': 'date'}),
            'filters': forms.Textarea(attrs={'rows': 3}),
        }


class ReportFilterForm(forms.Form):
    report_type = forms.ChoiceField(
        choices=[('', 'All')] + Report.REPORT_TYPES,
        required=False
    )
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    status = forms.ChoiceField(
        choices=[('', 'All')] + Report.STATUS_CHOICES,
        required=False
    )
