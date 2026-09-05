from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Address, VendorProfile

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone_number = forms.CharField(max_length=20, required=False)

    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'phone_number', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('A user with this email already exists.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email'].lower()
        if commit:
            user.save()
        return user


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'phone_number', 'avatar',
                  'date_of_birth', 'gender', 'newsletter_subscribed']


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['label', 'first_name', 'last_name', 'company', 'address_line1',
                  'address_line2', 'city', 'state', 'postal_code', 'country', 'phone',
                  'is_default', 'is_billing', 'is_shipping']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def save(self, commit=True):
        address = super().save(commit=False)
        if self.user:
            address.user = self.user
        if commit:
            address.save()
        return address


class VendorProfileForm(forms.ModelForm):
    class Meta:
        model = VendorProfile
        fields = ['shop_name', 'shop_description', 'shop_logo', 'shop_banner',
                  'tax_id', 'business_type', 'website', 'shipping_policy',
                  'return_policy', 'avg_processing_time']


class UserSearchForm(forms.Form):
    email = forms.EmailField(required=False)
    role = forms.ChoiceField(
        choices=[('', 'All')] + User.ROLE_CHOICES if hasattr(User, 'ROLE_CHOICES') else [('', 'All')],
        required=False
    )
    is_active = forms.BooleanField(required=False)
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
