from django import forms
from .models import Review, ReviewReport


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['product', 'rating', 'title', 'body', 'pros', 'cons']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'body': forms.Textarea(attrs={'rows': 5}),
            'pros': forms.Textarea(attrs={'rows': 3}),
            'cons': forms.Textarea(attrs={'rows': 3}),
        }


class ReviewReportForm(forms.ModelForm):
    class Meta:
        model = ReviewReport
        fields = ['reason', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class ReviewFilterForm(forms.Form):
    RATING_CHOICES = [('', 'All')] + [(i, f'{i} Stars') for i in range(1, 6)]
    rating = forms.ChoiceField(choices=RATING_CHOICES, required=False)
    verified = forms.BooleanField(required=False)
    with_images = forms.BooleanField(required=False)
    sort = forms.ChoiceField(
        choices=[
            ('-created_at', 'Newest'),
            ('helpful', 'Most Helpful'),
            ('-rating', 'Highest Rating'),
            ('rating', 'Lowest Rating'),
        ],
        required=False
    )
