from django import forms
from django.contrib.auth import get_user_model

from constants.constant import UserRoles
from constants.form_styles import (
    BASE_INPUT,
    BASE_SELECT,
    BASE_TEXTAREA,
    FORM_GROUP,
)

User = get_user_model()


class UserEditForm(forms.ModelForm):
    """Form for editing user information by managers."""
    
    class Meta:
        model = User
        fields = ['email', 'role', 'is_active']
        widgets = {
            'email': forms.EmailInput(attrs={'class': BASE_INPUT}),
            'role': forms.Select(attrs={'class': BASE_SELECT}),
            'is_active': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500'}),
        }
        labels = {
            'email': 'Correo Electrónico',
            'role': 'Rol',
            'is_active': 'Usuario Activo',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Exclude manager role from choices for security
        role_choices = [(k, v) for k, v in UserRoles.get_choices() if k != UserRoles.MANAGER]
        self.fields['role'].choices = role_choices


class ProfileEditForm(forms.ModelForm):
    """Form for editing user profile information by managers."""
    
    class Meta:
        model = User.profile.related.related_model
        fields = ['first_name', 'last_name', 'bio']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': BASE_INPUT}),
            'last_name': forms.TextInput(attrs={'class': BASE_INPUT}),
            'bio': forms.Textarea(attrs={'class': BASE_TEXTAREA, 'rows': 3}),
        }
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'bio': 'Biografía',
        }


class UserFilterForm(forms.Form):
    """Form for filtering users by role."""
    
    ROLE_CHOICES = [('', 'Todos los roles')] + list(UserRoles.get_choices())
    
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': BASE_SELECT}),
        label='Filtrar por rol'
    )
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': BASE_INPUT,
            'placeholder': 'Buscar por email o nombre...'
        }),
        label='Buscar'
    )