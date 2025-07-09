from django import forms
from django.contrib.auth import get_user_model

from constants.constant import UserRoles
from constants.form_styles import (
    BASE_INPUT,
    BASE_SELECT,
    BASE_TEXTAREA,
    FORM_GROUP,
    FILE_INPUT,
    MULTIPLE_SELECT,
)
from blog.models import Post, Category, Tag

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
        role_choices = [(k, v) for k, v in UserRoles.get_choices()
                        if k != UserRoles.MANAGER]
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


class BlogPostForm(forms.ModelForm):
    """Formulario personalizado para posts del blog con estilos uniformes."""

    class Meta:
        model = Post
        fields = ['title', 'slug', 'introduction', 'body', 'featured_image',
                  'status', 'category', 'tags', 'meta_title', 'meta_description']
        widgets = {
            'title': forms.TextInput(attrs={'class': BASE_INPUT}),
            'slug': forms.TextInput(attrs={'class': BASE_INPUT}),
            'introduction': forms.Textarea(attrs={'class': BASE_TEXTAREA, 'rows': 3}),
            # Hidden for Quill editor
            'body': forms.Textarea(attrs={'class': 'hidden'}),
            'featured_image': forms.FileInput(attrs={'class': FILE_INPUT}),
            'status': forms.Select(attrs={'class': BASE_SELECT}),
            'category': forms.Select(attrs={'class': BASE_SELECT}),
            'tags': forms.SelectMultiple(attrs={'class': MULTIPLE_SELECT}),
            'meta_title': forms.TextInput(attrs={'class': BASE_INPUT}),
            'meta_description': forms.Textarea(attrs={'class': BASE_TEXTAREA, 'rows': 3}),
        }


class CategoryForm(forms.ModelForm):
    """Formulario personalizado para categorías con estilos uniformes."""

    class Meta:
        model = Category
        fields = ['name', 'slug', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': BASE_INPUT}),
            'slug': forms.TextInput(attrs={'class': BASE_INPUT}),
            'description': forms.Textarea(attrs={'class': BASE_TEXTAREA, 'rows': 3}),
        }


class TagForm(forms.ModelForm):
    """Formulario personalizado para etiquetas con estilos uniformes."""

    class Meta:
        model = Tag
        fields = ['name', 'slug', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': BASE_INPUT}),
            'slug': forms.TextInput(attrs={'class': BASE_INPUT}),
            'description': forms.Textarea(attrs={'class': BASE_TEXTAREA, 'rows': 3}),
        }
