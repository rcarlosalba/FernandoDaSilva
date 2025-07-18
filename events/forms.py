from django import forms
from django.forms import inlineformset_factory
from django.utils import timezone
from django.core.exceptions import ValidationError
from constants import form_styles
from .models import Event, Category, PaymentMethod, Registration, Payment, Survey, SurveyQuestion, SurveyQuestionOption, SurveyQuestionResponse


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
            'send_survey', 'survey'
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
            'survey': forms.Select(attrs={'class': form_styles.BASE_SELECT}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer campos opcionales según el tipo de evento
        if self.instance.pk:
            if self.instance.event_type == 'online':
                self.fields['location'].required = False
            else:
                self.fields['event_link'].required = False

        # Filtrar encuestas activas para el campo survey
        self.fields['survey'].queryset = Survey.objects.filter(status='active')
        self.fields['survey'].empty_label = "Seleccionar encuesta (opcional)"

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


# ====== FORMULARIOS DE ENCUESTAS ======

class SurveyForm(forms.ModelForm):
    """
    Formulario para crear y editar encuestas.
    """
    class Meta:
        model = Survey
        fields = ['title', 'description', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': form_styles.BASE_INPUT}),
            'description': forms.Textarea(attrs={
                'class': form_styles.BASE_TEXTAREA,
                'rows': 4,
                'placeholder': 'Descripción opcional de la encuesta...'
            }),
            'status': forms.Select(attrs={'class': form_styles.BASE_SELECT}),
        }

    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title.strip()) < 3:
            raise ValidationError(
                "El título debe tener al menos 3 caracteres.")
        return title.strip()


class SurveyQuestionForm(forms.ModelForm):
    """
    Formulario para crear y editar preguntas de encuesta.
    """
    class Meta:
        model = SurveyQuestion
        fields = ['text', 'question_type', 'order', 'required']
        widgets = {
            'text': forms.TextInput(attrs={
                'class': form_styles.BASE_INPUT,
                'placeholder': 'Escribe tu pregunta aquí...'
            }),
            'question_type': forms.Select(attrs={'class': form_styles.BASE_SELECT}),
            'order': forms.NumberInput(attrs={
                'class': form_styles.BASE_INPUT,
                'min': '1'
            }),
            'required': forms.CheckboxInput(attrs={'class': form_styles.BASE_CHECKBOX}),
        }

    def clean_text(self):
        text = self.cleaned_data['text']
        if len(text.strip()) < 5:
            raise ValidationError(
                "La pregunta debe tener al menos 5 caracteres.")
        return text.strip()

    def clean_order(self):
        order = self.cleaned_data['order']
        if order < 1:
            raise ValidationError("El orden debe ser mayor a 0.")
        return order


class SurveyQuestionOptionForm(forms.ModelForm):
    """
    Formulario para crear y editar opciones de preguntas de opciones múltiples.
    """
    class Meta:
        model = SurveyQuestionOption
        fields = ['text', 'order']
        widgets = {
            'text': forms.TextInput(attrs={
                'class': form_styles.BASE_INPUT,
                'placeholder': 'Escribe la opción aquí...'
            }),
            'order': forms.NumberInput(attrs={
                'class': form_styles.BASE_INPUT,
                'min': '1'
            }),
        }

    def clean_text(self):
        text = self.cleaned_data['text']
        if len(text.strip()) < 1:
            raise ValidationError("La opción no puede estar vacía.")
        return text.strip()

    def clean_order(self):
        order = self.cleaned_data['order']
        if order < 1:
            raise ValidationError("El orden debe ser mayor a 0.")
        return order


class SurveyQuestionFormSet(forms.BaseInlineFormSet):
    """
    FormSet para gestionar múltiples preguntas de una encuesta.
    """

    def clean(self):
        super().clean()

        # Verificar que hay al menos una pregunta
        if not any(form.cleaned_data and not form.cleaned_data.get('DELETE', False)
                   for form in self.forms):
            raise ValidationError(
                "La encuesta debe tener al menos una pregunta.")

        # Verificar que no hay órdenes duplicados
        orders = []
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                order = form.cleaned_data.get('order')
                if order in orders:
                    raise ValidationError(
                        "No puede haber preguntas con el mismo orden.")
                orders.append(order)


class SurveyQuestionOptionFormSet(forms.BaseInlineFormSet):
    """
    FormSet para gestionar múltiples opciones de una pregunta de opciones múltiples.
    """

    def clean(self):
        super().clean()

        # Verificar que hay al menos dos opciones para preguntas de opciones múltiples
        valid_options = []
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                valid_options.append(form.cleaned_data)

        if len(valid_options) < 2:
            raise ValidationError(
                "Las preguntas de opciones múltiples deben tener al menos 2 opciones.")

        # Verificar que no hay órdenes duplicados
        orders = []
        for option in valid_options:
            order = option.get('order')
            if order in orders:
                raise ValidationError(
                    "No puede haber opciones con el mismo orden.")
            orders.append(order)


class SurveyResponseForm(forms.Form):
    """
    Formulario dinámico para responder una encuesta.
    """

    def __init__(self, survey_response, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.survey_response = survey_response

        # Crear campos dinámicos para cada pregunta
        for question in survey_response.survey.questions.all():
            field_name = f'question_{question.id}'

            if question.question_type == 'text':
                self.fields[field_name] = forms.CharField(
                    required=question.required,
                    widget=forms.Textarea(attrs={
                        'class': form_styles.BASE_TEXTAREA,
                        'rows': 3,
                        'placeholder': 'Escribe tu respuesta aquí...'
                    })
                )

            elif question.question_type == 'scale':
                self.fields[field_name] = forms.ChoiceField(
                    required=question.required,
                    choices=[(i, str(i)) for i in range(1, 6)],
                    widget=forms.RadioSelect(attrs={'class': 'space-y-2'})
                )

            elif question.question_type == 'multiple_choice':
                choices = [(option.id, option.text)
                           for option in question.options.all()]
                self.fields[field_name] = forms.ChoiceField(
                    required=question.required,
                    choices=choices,
                    widget=forms.RadioSelect(attrs={'class': 'space-y-2'})
                )

            # Agregar label personalizado
            self.fields[field_name].label = question.text
            if question.required:
                self.fields[field_name].label += ' *'

    def save(self):
        """Guarda las respuestas a la base de datos."""
        for field_name, value in self.cleaned_data.items():
            if field_name.startswith('question_'):
                question_id = int(field_name.split('_')[1])
                question = SurveyQuestion.objects.get(id=question_id)

                # Crear o actualizar la respuesta
                response, created = SurveyQuestionResponse.objects.get_or_create(
                    survey_response=self.survey_response,
                    question=question
                )

                # Guardar el valor según el tipo de pregunta
                if question.question_type == 'text':
                    response.text_response = value
                elif question.question_type == 'scale':
                    response.scale_response = int(value)
                elif question.question_type == 'multiple_choice':
                    response.selected_option = SurveyQuestionOption.objects.get(
                        id=int(value))

                response.save()

        # Marcar la encuesta como completada
        self.survey_response.mark_completed()


class EventSurveyForm(forms.ModelForm):
    """
    Formulario para asignar encuestas a eventos.
    """
    class Meta:
        model = Event
        fields = ['survey', 'send_survey']
        widgets = {
            'survey': forms.Select(attrs={'class': form_styles.BASE_SELECT}),
            'send_survey': forms.CheckboxInput(attrs={'class': form_styles.BASE_CHECKBOX}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo encuestas activas
        self.fields['survey'].queryset = Survey.objects.filter(status='active')
        self.fields['survey'].empty_label = "Seleccionar encuesta (opcional)"

    def clean(self):
        cleaned_data = super().clean()
        send_survey = cleaned_data.get('send_survey')
        survey = cleaned_data.get('survey')

        if send_survey and not survey:
            raise ValidationError(
                "Debe seleccionar una encuesta para enviar encuestas de satisfacción."
            )

        return cleaned_data


# Crear los formsets usando inlineformset_factory
SurveyQuestionFormSet = inlineformset_factory(
    Survey,  # Modelo padre
    SurveyQuestion,  # Modelo hijo
    form=SurveyQuestionForm,
    formset=SurveyQuestionFormSet,
    extra=1,  # Número de formularios vacíos adicionales
    can_delete=True,  # Permitir eliminar preguntas
)

SurveyQuestionOptionFormSet = inlineformset_factory(
    SurveyQuestion,  # Modelo padre
    SurveyQuestionOption,  # Modelo hijo
    form=SurveyQuestionOptionForm,
    formset=SurveyQuestionOptionFormSet,
    extra=2,  # Número de formularios vacíos adicionales (mínimo 2 opciones)
    can_delete=True,  # Permitir eliminar opciones
    min_num=2,  # Mínimo número de formularios requeridos
)
