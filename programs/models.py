"""
Models for the programs app.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from constants.constant import (
    ASSIGNMENT_STATUS_CHOICES, MATERIAL_TYPE_CHOICES,
    FEEDBACK_QUESTION_TYPE_CHOICES
)

User = get_user_model()


class Program(models.Model):
    """
    Represents a complete course (e.g., "Maestría Emocional").
    The main container unit that contains multiple modules.
    """
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(verbose_name="Descripción")
    cover_image = models.ImageField(
        upload_to='programs/covers/',
        blank=True,
        null=True,
        verbose_name="Imagen de portada"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de actualización")

    class Meta:
        verbose_name = "Programa"
        verbose_name_plural = "Programas"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def total_sessions(self):
        """Returns the total number of sessions in this program."""
        return sum(module.sessions.count() for module in self.modules.all())


class Module(models.Model):
    """
    A chapter or thematic section within a Program.
    Groups a set of related lessons (e.g., "Módulo 1: Autoconocimiento").
    """
    program = models.ForeignKey(
        Program,
        on_delete=models.CASCADE,
        related_name='modules',
        verbose_name="Programa"
    )
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(verbose_name="Descripción")
    order = models.PositiveIntegerField(verbose_name="Orden de aparición")
    congratulation_message = models.TextField(
        blank=True,
        verbose_name="Mensaje de felicitación"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de actualización")

    class Meta:
        verbose_name = "Módulo"
        verbose_name_plural = "Módulos"
        ordering = ['order']
        unique_together = ['program', 'order']

    def __str__(self):
        return f"{self.program.title} - {self.title}"


class Session(models.Model):
    """
    The atomic learning unit where the student interacts with content.
    Presents educational content (e.g., "Introducción al Eneagrama").
    """
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name='sessions',
        verbose_name="Módulo"
    )
    title = models.CharField(max_length=200, verbose_name="Título")
    order = models.PositiveIntegerField(verbose_name="Orden de aparición")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de actualización")

    class Meta:
        verbose_name = "Sesión"
        verbose_name_plural = "Sesiones"
        ordering = ['order']
        unique_together = ['module', 'order']

    def __str__(self):
        return f"{self.module.title} - {self.title}"


class Material(models.Model):
    """
    The specific content within a Session.
    Delivers information in various formats. All materials are optional,
    but each session must contain at least one.
    """
    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        related_name='materials',
        verbose_name="Sesión"
    )
    type = models.CharField(
        max_length=20,
        choices=MATERIAL_TYPE_CHOICES,
        verbose_name="Tipo"
    )
    title = models.CharField(max_length=200, verbose_name="Título")
    video_url = models.URLField(
        blank=True, null=True, verbose_name="URL del video")
    audio_url = models.URLField(
        blank=True, null=True, verbose_name="URL del audio")
    reading_content = models.TextField(
        blank=True, null=True, verbose_name="Contenido de lectura")
    file = models.FileField(
        upload_to='programs/materials/',
        blank=True,
        null=True,
        verbose_name="Archivo"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de actualización")

    class Meta:
        verbose_name = "Material"
        verbose_name_plural = "Materiales"
        ordering = ['created_at']

    def __str__(self):
        return f"{self.session.title} - {self.title}"

    def clean(self):
        """Validate that at least one content field is provided based on type."""
        from django.core.exceptions import ValidationError

        if self.type == 'video' and not self.video_url:
            raise ValidationError(
                'La URL del video es requerida para materiales de video.')
        elif self.type == 'audio' and not self.audio_url:
            raise ValidationError(
                'La URL del audio es requerida para materiales de audio.')
        elif self.type == 'reading' and not self.reading_content:
            raise ValidationError(
                'El contenido de lectura es requerido para materiales de lectura.')
        elif self.type == 'file' and not self.file:
            raise ValidationError(
                'El archivo es requerido para materiales de archivo.')


class Assignment(models.Model):
    """
    The entity that connects a Student with a Program.
    Formalizes enrollment and allows individual progress tracking.
    """
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='program_assignments',
        verbose_name="Estudiante"
    )
    program = models.ForeignKey(
        Program,
        on_delete=models.CASCADE,
        related_name='assignments',
        verbose_name="Programa"
    )
    status = models.CharField(
        max_length=20,
        choices=ASSIGNMENT_STATUS_CHOICES,
        default='active',
        verbose_name="Estado"
    )
    progress_percentage = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Porcentaje de progreso"
    )
    assigned_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de asignación")
    completed_at = models.DateTimeField(
        blank=True, null=True, verbose_name="Fecha de finalización")
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de actualización")

    class Meta:
        verbose_name = "Asignación"
        verbose_name_plural = "Asignaciones"
        unique_together = ['student', 'program']
        ordering = ['-assigned_at']

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.program.title}"

    def update_progress(self):
        """Calculate and update the progress percentage based on completed sessions."""
        total_sessions = self.program.total_sessions
        if total_sessions == 0:
            self.progress_percentage = 0
        else:
            completed_sessions = self.completed_sessions.count()
            self.progress_percentage = int(
                (completed_sessions / total_sessions) * 100)

        # Update status if completed
        if self.progress_percentage == 100 and self.status == 'active':
            self.status = 'completed'
            self.completed_at = timezone.now()

        self.save()


class SessionCompletion(models.Model):
    """
    Tracks which sessions have been completed by each student.
    """
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='completed_sessions',
        verbose_name="Asignación"
    )
    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        related_name='completions',
        verbose_name="Sesión"
    )
    completed_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de finalización")

    class Meta:
        verbose_name = "Finalización de sesión"
        verbose_name_plural = "Finalizaciones de sesiones"
        unique_together = ['assignment', 'session']
        ordering = ['completed_at']

    def __str__(self):
        return f"{self.assignment.student.get_full_name()} - {self.session.title}"


class Comment(models.Model):
    """
    The unit of social interaction and reflection in each Session.
    Encourages discussion and support among students.
    """
    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name="Sesión"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='program_comments',
        verbose_name="Autor"
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='replies',
        verbose_name="Comentario padre"
    )
    content = models.TextField(verbose_name="Contenido")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de actualización")

    class Meta:
        verbose_name = "Comentario"
        verbose_name_plural = "Comentarios"
        ordering = ['created_at']

    def __str__(self):
        return f"{self.author.get_full_name()} - {self.session.title}"

    def clean(self):
        """Validate that only two levels of nesting are allowed."""
        from django.core.exceptions import ValidationError

        if self.parent and self.parent.parent:
            raise ValidationError('Solo se permiten dos niveles de anidación.')


class FinalFeedback(models.Model):
    """
    A form to collect the Student's opinion at the end of the program.
    Serves as a qualitative feedback tool for the Manager.
    """
    program = models.OneToOneField(
        Program,
        on_delete=models.CASCADE,
        related_name='final_feedback',
        verbose_name="Programa"
    )
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(verbose_name="Descripción")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de actualización")

    class Meta:
        verbose_name = "Evaluación final"
        verbose_name_plural = "Evaluaciones finales"

    def __str__(self):
        return f"Evaluación final - {self.program.title}"


class FeedbackQuestion(models.Model):
    """
    Questions within a FinalFeedback form.
    """
    final_feedback = models.ForeignKey(
        FinalFeedback,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name="Evaluación final"
    )
    question = models.CharField(max_length=500, verbose_name="Pregunta")
    type = models.CharField(
        max_length=20,
        choices=FEEDBACK_QUESTION_TYPE_CHOICES,
        verbose_name="Tipo"
    )
    required = models.BooleanField(default=True, verbose_name="Obligatoria")
    order = models.PositiveIntegerField(default=0, verbose_name="Orden")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de creación")

    class Meta:
        verbose_name = "Pregunta de evaluación"
        verbose_name_plural = "Preguntas de evaluación"
        ordering = ['order']

    def __str__(self):
        return f"{self.final_feedback.program.title} - {self.question[:50]}"


class FeedbackResponse(models.Model):
    """
    Individual responses to feedback questions.
    """
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='feedback_responses',
        verbose_name="Asignación"
    )
    question = models.ForeignKey(
        FeedbackQuestion,
        on_delete=models.CASCADE,
        related_name='responses',
        verbose_name="Pregunta"
    )
    response = models.TextField(verbose_name="Respuesta")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de creación")

    class Meta:
        verbose_name = "Respuesta de evaluación"
        verbose_name_plural = "Respuestas de evaluación"
        unique_together = ['assignment', 'question']
        ordering = ['created_at']

    def __str__(self):
        return f"{self.assignment.student.get_full_name()} - {self.question.question[:30]}"
