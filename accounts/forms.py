from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.core.exceptions import ValidationError

from constants.form_styles import BASE_INPUT, PASSWORD_INPUT, SEARCH_INPUT, BASE_TEXTAREA, FILE_INPUT
from .models import Profile, User


class SubscriberRegistrationForm(forms.ModelForm):
    """
    Form for new subscribers to register with only their email address.
    """

    class Meta:
        model = User
        fields = ["email"]
        widgets = {
            "email": forms.EmailInput(attrs={
                "placeholder": "tu@correo.com",
                "class": SEARCH_INPUT
            })
        }


class CompleteProfileForm(forms.ModelForm):
    """
    Form for subscribers to complete their profile, set a password,
    and become a member.
    """

    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Crea una contraseña",
                "class": PASSWORD_INPUT
            }
        ),
    )
    confirm_password = forms.CharField(
        label="Confirmar Contraseña",
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Confirma tu contraseña",
                "class": PASSWORD_INPUT
            }
        ),
    )

    class Meta:
        model = Profile
        fields = ["first_name", "last_name", "bio"]
        widgets = {
            "first_name": forms.TextInput(attrs={
                "placeholder": "Nombre",
                "class": BASE_INPUT
            }),
            "last_name": forms.TextInput(attrs={
                "placeholder": "Apellidos",
                "class": BASE_INPUT
            }),
            "bio": forms.Textarea(attrs={
                "placeholder": "Comparte qué te trae aquí, tu momento actual, tus búsquedas...",
                "rows": 4,
                "class": BASE_TEXTAREA + " resize-none"
            }),
        }

    def clean_confirm_password(self):
        """
        Validates that the two password fields match.
        """
        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            raise ValidationError("Las contraseñas no coinciden.")
        return confirm_password


class LoginForm(AuthenticationForm):
    """
    Custom login form to use email as username and set Spanish labels.
    """

    username = forms.EmailField(
        label="Correo Electrónico",
        widget=forms.EmailInput(
            attrs={
                "autofocus": True,
                "placeholder": "email@ejemplo.com",
                "class": SEARCH_INPUT
            }
        ),
    )
    password = forms.CharField(
        label="Contraseña",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "current-password",
                "placeholder": "Tu contraseña",
                "class": SEARCH_INPUT
            }
        ),
    )


class ProfileEditForm(forms.ModelForm):
    """
    Form for users to edit their profile information.
    """

    class Meta:
        model = Profile
        fields = ["first_name", "last_name", "bio", "avatar"]
        widgets = {
            "first_name": forms.TextInput(attrs={
                "placeholder": "Nombre",
                "class": BASE_INPUT
            }),
            "last_name": forms.TextInput(attrs={
                "placeholder": "Apellidos",
                "class": BASE_INPUT
            }),
            "bio": forms.Textarea(attrs={
                "placeholder": "Comparte un poco sobre ti, tu momento actual, tus búsquedas...",
                "rows": 5,
                "class": BASE_TEXTAREA + " resize-none"
            }),
            "avatar": forms.FileInput(attrs={
                "class": FILE_INPUT,
                "accept": "image/jpeg,image/jpg,image/png"
            }),
        }


class CustomPasswordChangeForm(PasswordChangeForm):
    """
    Formulario de cambio de contraseña con estilos Tailwind.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': BASE_INPUT
            })
