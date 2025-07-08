from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'email', 'body']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'name mb-3 form-control', 'style': 'width: 100%;'}),
            'email': forms.EmailInput(attrs={'class': 'email mb-3 form-control', 'style': 'width: 100%;'}),
            'body': forms.Textarea(attrs={'class': 'message mb-3 form-control', 'row': 5}),
            'parent': forms.HiddenInput()
        }


class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'name mb-3 form-control',
            'style': 'width: 100%;',
            'placeholder': 'Your Name'
        })
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'email mb-3 form-control',
            'style': 'width: 100%;',
            'placeholder': 'Your Email'
        })
    )

    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'message mb-3 form-control',
            'rows': 5,
            'placeholder': 'Your Message'
        })
    )
