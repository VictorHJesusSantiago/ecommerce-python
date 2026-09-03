from django import forms
from .models import SavedSearch


class SearchForm(forms.Form):
    q = forms.CharField(max_length=500, required=True)
    category = forms.UUIDField(required=False)
    brand = forms.UUIDField(required=False)
    min_price = forms.DecimalField(required=False)
    max_price = forms.DecimalField(required=False)
    rating = forms.IntegerField(required=False, min_value=1, max_value=5)
    in_stock = forms.BooleanField(required=False)
    sort_by = forms.ChoiceField(
        choices=[
            ('relevance', 'Relevance'),
            ('price_asc', 'Price: Low to High'),
            ('price_desc', 'Price: High to Low'),
            ('rating', 'Rating'),
            ('newest', 'Newest'),
            ('popular', 'Popular'),
        ],
        required=False
    )


class SavedSearchForm(forms.ModelForm):
    class Meta:
        model = SavedSearch
        fields = ['name', 'query', 'filters', 'notify_new_results']
        widgets = {
            'filters': forms.Textarea(attrs={'rows': 3}),
        }
