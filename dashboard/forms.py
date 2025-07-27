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
from programs.models import (
    Program, Module, Session, Material, Assignment,
    FinalFeedback, FeedbackQuestion
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


# Program Management Forms

class ProgramForm(forms.ModelForm):
    """Formulario para crear y editar programas."""

    class Meta:
        model = Program
        fields = ['title', 'description', 'cover_image']
        widgets = {
            'title': forms.TextInput(attrs={'class': BASE_INPUT}),
            'description': forms.Textarea(attrs={'class': BASE_TEXTAREA, 'rows': 4}),
            'cover_image': forms.FileInput(attrs={'class': FILE_INPUT}),
        }
        labels = {
            'title': 'Título del Programa',
            'description': 'Descripción',
            'cover_image': 'Imagen de Portada',
        }


class ModuleForm(forms.ModelForm):
    """Formulario para crear y editar módulos."""

    class Meta:
        model = Module
        fields = ['title', 'description', 'order', 'congratulation_message']
        widgets = {
            'title': forms.TextInput(attrs={'class': BASE_INPUT}),
            'description': forms.Textarea(attrs={'class': BASE_TEXTAREA, 'rows': 3}),
            'order': forms.NumberInput(attrs={'class': BASE_INPUT}),
            'congratulation_message': forms.Textarea(attrs={'class': BASE_TEXTAREA, 'rows': 3}),
        }
        labels = {
            'title': 'Título del Módulo',
            'description': 'Descripción',
            'order': 'Orden de Aparición',
            'congratulation_message': 'Mensaje de Felicitación',
        }


class SessionForm(forms.ModelForm):
    """Formulario para crear y editar sesiones."""

    class Meta:
        model = Session
        fields = ['title', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': BASE_INPUT}),
            'order': forms.NumberInput(attrs={'class': BASE_INPUT}),
        }
        labels = {
            'title': 'Título de la Sesión',
            'order': 'Orden de Aparición',
        }


class MaterialForm(forms.ModelForm):
    """Formulario para crear y editar materiales."""

    class Meta:
        model = Material
        fields = ['type', 'title', 'video_url',
                  'audio_url', 'reading_content', 'file']
        widgets = {
            'type': forms.Select(attrs={'class': BASE_SELECT}),
            'title': forms.TextInput(attrs={'class': BASE_INPUT}),
            'video_url': forms.URLInput(attrs={'class': BASE_INPUT}),
            'audio_url': forms.URLInput(attrs={'class': BASE_INPUT}),
            'reading_content': forms.Textarea(attrs={'class': BASE_TEXTAREA, 'rows': 6}),
            'file': forms.FileInput(attrs={'class': FILE_INPUT}),
        }
        labels = {
            'type': 'Tipo de Material',
            'title': 'Título del Material',
            'video_url': 'URL del Video',
            'audio_url': 'URL del Audio',
            'reading_content': 'Contenido de Lectura',
            'file': 'Archivo',
        }

    def clean(self):
        cleaned_data = super().clean()
        material_type = cleaned_data.get('type')

        # Validar que al menos un campo de contenido esté proporcionado según el tipo
        if material_type == 'video' and not cleaned_data.get('video_url'):
            raise forms.ValidationError(
                'La URL del video es requerida para materiales de video.')
        elif material_type == 'audio' and not cleaned_data.get('audio_url'):
            raise forms.ValidationError(
                'La URL del audio es requerida para materiales de audio.')
        elif material_type == 'reading' and not cleaned_data.get('reading_content'):
            raise forms.ValidationError(
                'El contenido de lectura es requerido para materiales de lectura.')
        elif material_type == 'file' and not cleaned_data.get('file'):
            raise forms.ValidationError(
                'El archivo es requerido para materiales de archivo.')

        return cleaned_data


class AssignmentForm(forms.ModelForm):
    """Formulario para crear y editar asignaciones."""

    class Meta:
        model = Assignment
        fields = ['student', 'program', 'status']
        widgets = {
            'student': forms.Select(attrs={'class': BASE_SELECT}),
            'program': forms.Select(attrs={'class': BASE_SELECT}),
            'status': forms.Select(attrs={'class': BASE_SELECT}),
        }
        labels = {
            'student': 'Estudiante',
            'program': 'Programa',
            'status': 'Estado',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo estudiantes
        self.fields['student'].queryset = User.objects.filter(
            role=UserRoles.STUDENT)


class FinalFeedbackForm(forms.ModelForm):
    """Formulario para crear y editar evaluaciones finales."""

    class Meta:
        model = FinalFeedback
        fields = ['program', 'title', 'description']
        widgets = {
            'program': forms.Select(attrs={'class': BASE_SELECT}),
            'title': forms.TextInput(attrs={'class': BASE_INPUT}),
            'description': forms.Textarea(attrs={'class': BASE_TEXTAREA, 'rows': 4}),
        }
        labels = {
            'program': 'Programa',
            'title': 'Título de la Evaluación',
            'description': 'Descripción',
        }


class FeedbackQuestionForm(forms.ModelForm):
    """Formulario para crear y editar preguntas de evaluación."""

    class Meta:
        model = FeedbackQuestion
        fields = ['question', 'type', 'required', 'order']
        widgets = {
            'question': forms.TextInput(attrs={'class': BASE_INPUT}),
            'type': forms.Select(attrs={'class': BASE_SELECT}),
            'required': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500'}),
            'order': forms.NumberInput(attrs={'class': BASE_INPUT}),
        }
        labels = {
            'question': 'Pregunta',
            'type': 'Tipo de Pregunta',
            'required': 'Obligatoria',
            'order': 'Orden',
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
