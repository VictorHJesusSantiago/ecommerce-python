from django import forms
from .models import Page, Menu, MenuItem, FAQ, ContactMessage


class PageForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = ['title', 'slug', 'content', 'template', 'is_published',
                  'featured_image', 'parent', 'sort_order', 'show_in_menu',
                  'menu_label', 'meta_title', 'meta_description', 'meta_keywords']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10}),
            'meta_description': forms.Textarea(attrs={'rows': 3}),
        }
        prepopulated_fields = {'slug': ('title',)}


class MenuForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = ['name', 'slug', 'is_active']
        prepopulated_fields = {'slug': ('name',)}


class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ['menu', 'parent', 'title', 'url', 'page', 'target',
                  'sort_order', 'is_active', 'css_class']


class FAQForm(forms.ModelForm):
    class Meta:
        model = FAQ
        fields = ['question', 'answer', 'category', 'sort_order', 'is_active']
        widgets = {
            'answer': forms.Textarea(attrs={'rows': 5}),
        }


class ContactMessageForm(forms.Form):
    name = forms.CharField(max_length=200)
    email = forms.EmailField()
    phone = forms.CharField(max_length=20, required=False)
    subject = forms.CharField(max_length=300)
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 5}))
