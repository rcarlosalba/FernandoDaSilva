from django import forms
from accounts.models import User
from constants.form_styles import SEARCH_INPUT


class BookSubscriberForm(forms.ModelForm):
    """
    Form for book chapter download subscription.
    Creates a new subscriber user to download the first chapter.
    """

    email = forms.EmailField(
        label='Correo Electrónico',
        widget=forms.EmailInput(attrs={
            'class': SEARCH_INPUT,
            'placeholder': 'tu@email.com',
            'autocomplete': 'email',
        }),
        error_messages={
            'required': 'El correo electrónico es obligatorio',
            'invalid': 'Ingresa un correo electrónico válido',
        }
    )

    class Meta:
        model = User
        fields = ['email']

    def clean_email(self):
        """
        Validates that email doesn't already exist.
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                'Este correo ya está registrado. Revisa tu email para el link de descarga.'
            )
        return email

    def save(self, commit=True):
        """
        Creates a new subscriber user with no password.
        """
        user = super().save(commit=False)
        user.set_unusable_password()  # No password initially
        if commit:
            user.save()
        return user
