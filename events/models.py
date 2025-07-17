from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.urls import reverse
from constants.constant import (
    EVENT_STATUS_CHOICES, EVENT_TYPE_CHOICES, EVENT_MODALITY_CHOICES,
    PAYMENT_METHOD_TYPE_CHOICES, REGISTRATION_STATUS_CHOICES, PAYMENT_STATUS_CHOICES
)

User = get_user_model()


class Category(models.Model):
    """
    Categoría para clasificar eventos.
    """
    name = models.CharField(max_length=100, verbose_name="Nombre")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Slug")
    description = models.TextField(blank=True, verbose_name="Descripción")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Última actualización")

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('events:category_detail', kwargs={'slug': self.slug})

    @property
    def event_count(self):
        """Retorna el número de eventos en esta categoría."""
        return self.events.count()


class PaymentMethod(models.Model):
    """
    Método de pago configurable por el manager.
    """
    name = models.CharField(max_length=100, verbose_name="Nombre descriptivo")
    type = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_TYPE_CHOICES,
        verbose_name="Tipo"
    )
    instructions = models.TextField(verbose_name="Instrucciones/Datos")
    external_link = models.URLField(blank=True, verbose_name="Enlace externo")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Última actualización")

    class Meta:
        verbose_name = "Método de Pago"
        verbose_name_plural = "Métodos de Pago"
        ordering = ['name']

    def __str__(self):
        return self.name


class Event(models.Model):
    """
    Modelo principal para eventos.
    """
    title = models.CharField(max_length=200, verbose_name="Título")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="Slug")
    description = models.TextField(verbose_name="Descripción")
    featured_image = models.ImageField(
        upload_to='events/featured/',
        blank=True,
        verbose_name="Imagen de portada"
    )
    start_date = models.DateTimeField(verbose_name="Fecha y hora de inicio")
    end_date = models.DateTimeField(verbose_name="Fecha y hora de fin")
    event_type = models.CharField(
        max_length=20,
        choices=EVENT_TYPE_CHOICES,
        verbose_name="Tipo de evento"
    )
    modality = models.CharField(
        max_length=20,
        choices=EVENT_MODALITY_CHOICES,
        verbose_name="Modalidad"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Precio"
    )
    max_capacity = models.PositiveIntegerField(verbose_name="Cupo máximo")
    location = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Ubicación"
    )
    event_link = models.URLField(
        blank=True,
        verbose_name="Enlace del evento"
    )
    status = models.CharField(
        max_length=20,
        choices=EVENT_STATUS_CHOICES,
        default='draft',
        verbose_name="Estado"
    )
    send_survey = models.BooleanField(
        default=False,
        verbose_name="Enviar encuesta de satisfacción"
    )

    # Relaciones
    categories = models.ManyToManyField(
        Category,
        related_name='events',
        verbose_name="Categorías"
    )
    payment_methods = models.ManyToManyField(
        PaymentMethod,
        blank=True,
        related_name='events',
        verbose_name="Métodos de pago"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_events',
        verbose_name="Creado por"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Última actualización")

    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"
        ordering = ['-start_date']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('events:event_detail', kwargs={'slug': self.slug})

    @property
    def is_full(self):
        """Verifica si el evento está lleno."""
        return self.registrations.filter(status='accepted').count() >= self.max_capacity

    @property
    def available_spots(self):
        """Retorna el número de cupos disponibles."""
        registered = self.registrations.filter(status='accepted').count()
        return max(0, self.max_capacity - registered)

    @property
    def is_finished(self):
        """Verifica si el evento ya terminó."""
        from django.utils import timezone
        return timezone.now() > self.end_date

    @property
    def is_upcoming(self):
        """Verifica si el evento está por venir."""
        from django.utils import timezone
        return timezone.now() < self.start_date


class Registration(models.Model):
    """
    Inscripción de un participante a un evento.
    """
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='registrations',
        verbose_name="Evento"
    )
    full_name = models.CharField(
        max_length=200, verbose_name="Nombre completo")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Teléfono")
    status = models.CharField(
        max_length=20,
        choices=REGISTRATION_STATUS_CHOICES,
        default='pending',
        verbose_name="Estado"
    )
    registration_date = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de inscripción")
    notes = models.TextField(blank=True, verbose_name="Notas")

    class Meta:
        verbose_name = "Inscripción"
        verbose_name_plural = "Inscripciones"
        ordering = ['-registration_date']
        unique_together = ['event', 'email']

    def __str__(self):
        return f"{self.full_name} - {self.event.title}"

    @property
    def has_payment(self):
        """Verifica si la inscripción tiene un pago asociado."""
        return hasattr(self, 'payment')


class Payment(models.Model):
    """
    Registro de transacción de pago para una inscripción.
    """
    registration = models.OneToOneField(
        Registration,
        on_delete=models.CASCADE,
        related_name='payment',
        verbose_name="Inscripción"
    )
    payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name="Método de pago"
    )
    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending',
        verbose_name="Estado del pago"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Monto"
    )
    receipt = models.FileField(
        upload_to='payments/receipts/',
        blank=True,
        verbose_name="Comprobante"
    )
    verification_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de verificación"
    )
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_payments',
        verbose_name="Verificado por"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Última actualización")

    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        ordering = ['-created_at']

    def __str__(self):
        return f"Pago de {self.registration.full_name} - {self.registration.event.title}"

    def verify_payment(self, user):
        """Marca el pago como verificado."""
        from django.utils import timezone
        self.status = 'verified'
        self.verification_date = timezone.now()
        self.verified_by = user
        self.save()

        # Actualizar el estado de la inscripción
        self.registration.status = 'accepted'
        self.registration.save()
