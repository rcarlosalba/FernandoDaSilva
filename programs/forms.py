"""
Forms for the programs app.
"""
from django import forms
from django.core.exceptions import ValidationError
from .models import (
    Program, Module, Session, Material, Assignment,
    Comment, FinalFeedback, FeedbackQuestion, FeedbackResponse
)
from constants.form_styles import FORM_STYLES, BASE_TEXTAREA


class ProgramForm(forms.ModelForm):
    """Form for creating and editing programs."""

    class Meta:
        model = Program
        fields = ['title', 'description', 'cover_image']
        widgets = {
            'title': forms.TextInput(attrs={'class': FORM_STYLES['text']}),
            'description': forms.Textarea(attrs={'class': FORM_STYLES['textarea']}),
            'cover_image': forms.FileInput(attrs={'class': FORM_STYLES['file']}),
        }


class ModuleForm(forms.ModelForm):
    """Form for creating and editing modules."""

    class Meta:
        model = Module
        fields = ['title', 'description', 'order', 'congratulation_message']
        widgets = {
            'title': forms.TextInput(attrs={'class': FORM_STYLES['text']}),
            'description': forms.Textarea(attrs={'class': FORM_STYLES['textarea']}),
            'order': forms.NumberInput(attrs={'class': FORM_STYLES['number']}),
            'congratulation_message': forms.Textarea(attrs={'class': FORM_STYLES['textarea']}),
        }


class SessionForm(forms.ModelForm):
    """Form for creating and editing sessions."""

    class Meta:
        model = Session
        fields = ['title', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': FORM_STYLES['text']}),
            'order': forms.NumberInput(attrs={'class': FORM_STYLES['number']}),
        }


class MaterialForm(forms.ModelForm):
    """Form for creating and editing materials."""

    class Meta:
        model = Material
        fields = ['type', 'title', 'video_url',
                  'audio_url', 'reading_content', 'file']
        widgets = {
            'type': forms.Select(attrs={'class': FORM_STYLES['select']}),
            'title': forms.TextInput(attrs={'class': FORM_STYLES['text']}),
            'video_url': forms.URLInput(attrs={'class': FORM_STYLES['url']}),
            'audio_url': forms.URLInput(attrs={'class': FORM_STYLES['url']}),
            'reading_content': forms.Textarea(attrs={'class': FORM_STYLES['textarea']}),
            'file': forms.FileInput(attrs={'class': FORM_STYLES['file']}),
        }

    def clean(self):
        cleaned_data = super().clean()
        material_type = cleaned_data.get('type')

        # Validate that at least one content field is provided based on type
        if material_type == 'video' and not cleaned_data.get('video_url'):
            raise ValidationError(
                'La URL del video es requerida para materiales de video.')
        elif material_type == 'audio' and not cleaned_data.get('audio_url'):
            raise ValidationError(
                'La URL del audio es requerida para materiales de audio.')
        elif material_type == 'reading' and not cleaned_data.get('reading_content'):
            raise ValidationError(
                'El contenido de lectura es requerido para materiales de lectura.')
        elif material_type == 'file' and not cleaned_data.get('file'):
            raise ValidationError(
                'El archivo es requerido para materiales de archivo.')

        return cleaned_data


class AssignmentForm(forms.ModelForm):
    """Form for creating and editing assignments."""

    class Meta:
        model = Assignment
        fields = ['student', 'program', 'status']
        widgets = {
            'student': forms.Select(attrs={'class': FORM_STYLES['select']}),
            'program': forms.Select(attrs={'class': FORM_STYLES['select']}),
            'status': forms.Select(attrs={'class': FORM_STYLES['select']}),
        }


class CommentForm(forms.ModelForm):
    """Form for creating and editing comments."""

    class Meta:
        model = Comment
        fields = ['content', 'parent']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': BASE_TEXTAREA + ' resize-none',
                'rows': 3,
                'placeholder': 'Escribe tu comentario...'
            }),
            'parent': forms.HiddenInput(),
        }
        labels = {
            'content': 'Comentario',
        }

    def clean_parent(self):
        parent = self.cleaned_data.get('parent')
        if parent and parent.parent:
            raise ValidationError('Solo se permiten dos niveles de anidación.')
        return parent


class FinalFeedbackForm(forms.ModelForm):
    """Form for creating and editing final feedback forms."""

    class Meta:
        model = FinalFeedback
        fields = ['program', 'title', 'description']
        widgets = {
            'program': forms.Select(attrs={'class': FORM_STYLES['select']}),
            'title': forms.TextInput(attrs={'class': FORM_STYLES['text']}),
            'description': forms.Textarea(attrs={'class': FORM_STYLES['textarea']}),
        }


class FeedbackQuestionForm(forms.ModelForm):
    """Form for creating and editing feedback questions."""

    class Meta:
        model = FeedbackQuestion
        fields = ['question', 'type', 'required']
        widgets = {
            'question': forms.TextInput(attrs={'class': FORM_STYLES['text']}),
            'type': forms.Select(attrs={'class': FORM_STYLES['select']}),
            'required': forms.CheckboxInput(attrs={'class': FORM_STYLES['checkbox']}),
        }


class FeedbackResponseForm(forms.ModelForm):
    """Form for submitting feedback responses."""

    class Meta:
        model = FeedbackResponse
        fields = ['response']
        widgets = {
            'response': forms.Textarea(attrs={'class': FORM_STYLES['textarea']}),
        }
