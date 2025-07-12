from django import forms
from constants.form_styles import BASE_INPUT, BASE_TEXTAREA
from .models import Newsletter
from constants.constant import NEWSLETTER_STATUS_CHOICES


class NewsletterForm(forms.ModelForm):
    """
    Form for creating and editing newsletters.
    """

    class Meta:
        model = Newsletter
        fields = ['title', 'content']
        labels = {
            'title': 'Título',
            'content': 'Contenido (HTML)',
        }
        help_texts = {
            'title': 'Introduce el título del boletín',
            'content': 'Escribe el contenido del boletín en formato HTML',
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': BASE_INPUT,
                'placeholder': 'Introduce el título del boletín'
            }),
            'content': forms.Textarea(attrs={
                'class': BASE_TEXTAREA,
                'rows': 15,
                'placeholder': 'Escribe el contenido del boletín (HTML)',
                'id': 'newsletter-content'  # Para integración con Quill.js
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].required = True
        self.fields['content'].required = True


class NewsletterSearchForm(forms.Form):
    """
    Form for searching newsletters.
    """
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': BASE_INPUT,
            'placeholder': 'Search newsletters by title...'
        })
    )

    status = forms.ChoiceField(
        choices=[('', 'All Status')] + NEWSLETTER_STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': BASE_INPUT
        })
    )
