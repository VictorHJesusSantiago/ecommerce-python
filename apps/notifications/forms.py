from django import forms
from .models import EmailTemplate, Notification


class EmailTemplateForm(forms.ModelForm):
    class Meta:
        model = EmailTemplate
        fields = ['name', 'subject', 'template_file', 'is_active', 'description', 'variables']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'variables': forms.Textarea(attrs={'rows': 3}),
        }


class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['user', 'notification_type', 'priority', 'title', 'message',
                  'data', 'action_url', 'icon']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4}),
            'data': forms.Textarea(attrs={'rows': 3}),
        }


class TestEmailForm(forms.Form):
    recipient = forms.EmailField()
    template = forms.ModelChoiceField(queryset=EmailTemplate.objects.filter(is_active=True))
    context_data = forms.JSONField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3}),
        help_text='JSON context data for the template'
    )
