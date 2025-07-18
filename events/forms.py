from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError
from constants import form_styles
from .models import Event, Category, PaymentMethod, Registration, Payment


class EventForm(forms.ModelForm):
    """
    Formulario para crear y editar eventos.
    """
    class Meta:
        model = Event
        fields = [
            'title', 'slug', 'description', 'featured_image', 'start_date',
            'end_date', 'event_type', 'modality', 'price', 'max_capacity',
            'location', 'event_link', 'status', 'categories', 'payment_methods',
            'send_survey'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': form_styles.BASE_INPUT}),
            'slug': forms.TextInput(attrs={'class': form_styles.BASE_INPUT}),
            'description': forms.Textarea(attrs={'class': form_styles.BASE_TEXTAREA}),
            'featured_image': forms.FileInput(attrs={'class': form_styles.FILE_INPUT}),
            'start_date': forms.DateTimeInput(
                attrs={'class': form_styles.DATETIME_INPUT,
                       'type': 'datetime-local'}
            ),
            'end_date': forms.DateTimeInput(
                attrs={'class': form_styles.DATETIME_INPUT,
                       'type': 'datetime-local'}
            ),
            'event_type': forms.Select(attrs={'class': form_styles.BASE_SELECT}),
            'modality': forms.Select(attrs={'class': form_styles.BASE_SELECT}),
            'price': forms.NumberInput(attrs={'class': form_styles.CURRENCY_INPUT}),
            'max_capacity': forms.NumberInput(attrs={'class': form_styles.BASE_INPUT}),
            'location': forms.TextInput(attrs={'class': form_styles.BASE_INPUT}),
            'event_link': forms.URLInput(attrs={'class': form_styles.BASE_INPUT}),
            'status': forms.Select(attrs={'class': form_styles.BASE_SELECT}),
            'categories': forms.SelectMultiple(attrs={'class': form_styles.MULTIPLE_SELECT}),
            'payment_methods': forms.SelectMultiple(attrs={'class': form_styles.MULTIPLE_SELECT}),
            'send_survey': forms.CheckboxInput(attrs={'class': form_styles.BASE_CHECKBOX}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer campos opcionales según el tipo de evento
        if self.instance.pk:
            if self.instance.event_type == 'online':
                self.fields['location'].required = False
            else:
                self.fields['event_link'].required = False

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        modality = cleaned_data.get('modality')
        price = cleaned_data.get('price')
        event_type = cleaned_data.get('event_type')
        location = cleaned_data.get('location')
        event_link = cleaned_data.get('event_link')

        # Validar fechas
        if start_date and end_date:
            if start_date >= end_date:
                raise ValidationError(
                    "La fecha de fin debe ser posterior a la fecha de inicio.")

            if start_date < timezone.now():
                raise ValidationError(
                    "La fecha de inicio no puede ser en el pasado.")

        # Validar modalidad y precio
        if modality == 'paid' and (not price or price <= 0):
            raise ValidationError(
                "Los eventos de pago deben tener un precio mayor a 0.")

        # Validar campos según tipo de evento
        if event_type == 'presential' and not location:
            raise ValidationError(
                "Los eventos presenciales deben tener una ubicación.")

        if event_type == 'online' and not event_link:
            raise ValidationError("Los eventos online deben tener un enlace.")

        return cleaned_data


class CategoryForm(forms.ModelForm):
    """
    Formulario para crear y editar categorías.
    """
    class Meta:
        model = Category
        fields = ['name', 'slug', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': form_styles.BASE_INPUT}),
            'slug': forms.TextInput(attrs={'class': form_styles.BASE_INPUT}),
            'description': forms.Textarea(attrs={'class': form_styles.SMALL_TEXTAREA}),
        }

    def clean_name(self):
        name = self.cleaned_data['name']
        if len(name) < 2:
            raise ValidationError(
                "El nombre debe tener al menos 2 caracteres.")
        return name


class PaymentMethodForm(forms.ModelForm):
    """
    Formulario para crear y editar métodos de pago.
    """
    class Meta:
        model = PaymentMethod
        fields = ['name', 'type', 'instructions', 'external_link', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': form_styles.BASE_INPUT}),
            'type': forms.Select(attrs={'class': form_styles.BASE_SELECT}),
            'instructions': forms.Textarea(attrs={'class': form_styles.BASE_TEXTAREA}),
            'external_link': forms.URLInput(attrs={'class': form_styles.BASE_INPUT}),
            'is_active': forms.CheckboxInput(attrs={'class': form_styles.BASE_CHECKBOX}),
        }

    def clean(self):
        cleaned_data = super().clean()
        method_type = cleaned_data.get('type')
        external_link = cleaned_data.get('external_link')

        # Validar enlace externo solo para métodos de tipo external_link
        if method_type == 'external_link' and not external_link:
            raise ValidationError(
                "Los métodos de enlace externo deben tener una URL.")

        return cleaned_data


class RegistrationForm(forms.ModelForm):
    """
    Formulario para inscripciones públicas.
    """
    class Meta:
        model = Registration
        fields = ['full_name', 'email', 'phone', 'notes']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': form_styles.BASE_INPUT}),
            'email': forms.EmailInput(attrs={'class': form_styles.BASE_INPUT}),
            'phone': forms.TextInput(attrs={'class': form_styles.PHONE_INPUT}),
            'notes': forms.Textarea(attrs={
                'class': form_styles.BASE_TEXTAREA,
                'rows': 4,
                'placeholder': 'Información adicional que quieras compartir (opcional)'
            }),
        }

    def __init__(self, event=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event = event

    def clean_email(self):
        email = self.cleaned_data['email']
        if self.event and Registration.objects.filter(event=self.event, email=email).exists():
            raise ValidationError(
                "Ya existe una inscripción con este email para este evento.")
        return email

    def clean_full_name(self):
        full_name = self.cleaned_data['full_name']
        if len(full_name.strip()) < 3:
            raise ValidationError(
                "El nombre completo debe tener al menos 3 caracteres.")
        return full_name.strip()


class PaymentForm(forms.ModelForm):
    """
    Formulario para pagos de inscripciones.
    """
    class Meta:
        model = Payment
        fields = ['payment_method', 'receipt']
        widgets = {
            'payment_method': forms.Select(attrs={'class': form_styles.BASE_SELECT}),
            'receipt': forms.FileInput(attrs={'class': form_styles.FILE_INPUT}),
        }

    def __init__(self, registration=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.registration = registration

        # Filtrar métodos de pago activos y disponibles para el evento
        if registration and registration.event:
            self.fields['payment_method'].queryset = PaymentMethod.objects.filter(
                is_active=True,
                events=registration.event
            )

    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')
        receipt = cleaned_data.get('receipt')

        if payment_method and payment_method.type == 'transfer' and not receipt:
            raise ValidationError(
                "Para pagos por transferencia, debe subir el comprobante.")

        return cleaned_data

    def save(self, commit=True):
        payment = super().save(commit=False)
        if self.registration:
            payment.registration = self.registration
            payment.amount = self.registration.event.price
        if commit:
            payment.save()
        return payment


class EventFilterForm(forms.Form):
    """
    Formulario para filtrar eventos en la vista pública.
    """
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="Todas las categorías",
        widget=forms.Select(attrs={'class': form_styles.BASE_SELECT})
    )

    event_type = forms.ChoiceField(
        choices=[('', 'Todos los tipos')] +
        list(Event._meta.get_field('event_type').choices),
        required=False,
        widget=forms.Select(attrs={'class': form_styles.BASE_SELECT})
    )

    modality = forms.ChoiceField(
        choices=[('', 'Todas las modalidades')] +
        list(Event._meta.get_field('modality').choices),
        required=False,
        widget=forms.Select(attrs={'class': form_styles.BASE_SELECT})
    )

    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': form_styles.SEARCH_INPUT,
            'placeholder': 'Buscar eventos...'
        })
    )
