from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

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
                "class": "text-body w-full pl-10 pr-4 py-3 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary-300 focus:border-primary-300 transition-colors duration-300"
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
                "class": "text-body w-full px-4 py-3 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary-300 focus:border-primary-300 transition-colors duration-300"
            }
        ),
    )
    confirm_password = forms.CharField(
        label="Confirmar Contraseña",
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Confirma tu contraseña",
                "class": "text-body w-full px-4 py-3 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary-300 focus:border-primary-300 transition-colors duration-300"
            }
        ),
    )

    class Meta:
        model = Profile
        fields = ["first_name", "last_name", "bio"]
        widgets = {
            "first_name": forms.TextInput(attrs={
                "placeholder": "Nombre",
                "class": "text-body w-full px-4 py-3 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary-300 focus:border-primary-300 transition-colors duration-300"
            }),
            "last_name": forms.TextInput(attrs={
                "placeholder": "Apellidos",
                "class": "text-body w-full px-4 py-3 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary-300 focus:border-primary-300 transition-colors duration-300"
            }),
            "bio": forms.Textarea(attrs={
                "placeholder": "Comparte qué te trae aquí, tu momento actual, tus búsquedas...",
                "rows": 4,
                "class": "text-body w-full px-4 py-3 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary-300 focus:border-primary-300 transition-colors duration-300 resize-none"
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
                "class": "text-body w-full pl-10 pr-4 py-3 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary-300 focus:border-primary-300 transition-colors duration-300"
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
                "class": "text-body w-full pl-10 pr-4 py-3 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary-300 focus:border-primary-300 transition-colors duration-300"
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
                "class": "text-body w-full px-4 py-3 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary-300 focus:border-primary-300 transition-colors duration-300"
            }),
            "last_name": forms.TextInput(attrs={
                "placeholder": "Apellidos",
                "class": "text-body w-full px-4 py-3 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary-300 focus:border-primary-300 transition-colors duration-300"
            }),
            "bio": forms.Textarea(attrs={
                "placeholder": "Comparte un poco sobre ti, tu momento actual, tus búsquedas...",
                "rows": 5,
                "class": "text-body w-full px-4 py-3 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary-300 focus:border-primary-300 transition-colors duration-300 resize-none"
            }),
            "avatar": forms.FileInput(attrs={
                "class": "text-body w-full px-3 py-2 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary-300 focus:border-primary-300 transition-colors duration-300 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:bg-primary-100 file:text-primary-700 hover:file:bg-primary-200",
                "accept": "image/jpeg,image/jpg,image/png"
            }),
        }
