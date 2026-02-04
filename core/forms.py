from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'title', 'comment']
        widgets = {
            'rating': forms.HiddenInput(attrs={'id': 'rating-value'}),
            'title': forms.TextInput(attrs={
                'placeholder': 'Titre de votre avis (optionnel)',
                'class': 'review-title-input'
            }),
            'comment': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Dites-nous ce que vous pensez de ce produit...',
                'class': 'review-comment-input'
            }),
        }