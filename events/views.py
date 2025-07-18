from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from django.utils import timezone
from constants.constant import manager_required
from .models import Event, Category, PaymentMethod, Registration, Payment, Survey, SurveyQuestion, SurveyQuestionOption, SurveyResponse
from .forms import EventForm, CategoryForm, PaymentMethodForm, RegistrationForm, PaymentForm, SurveyForm, SurveyQuestionForm, SurveyQuestionOptionForm, SurveyQuestionFormSet, SurveyQuestionOptionFormSet, EventSurveyForm
from .utils import send_registration_confirmation_email, send_registration_approved_email, send_registration_rejected_email, create_survey_responses_for_event, send_survey_invitation_email


# ===== VISTAS DE EVENTOS =====

@manager_required
def event_list(request):
    """
    Lista de eventos para el dashboard.
    """
    events = Event.objects.select_related(
        'created_by').prefetch_related('categories').all()

    # Filtros
    status = request.GET.get('status')
    if status:
        events = events.filter(status=status)

    event_type = request.GET.get('event_type')
    if event_type:
        events = events.filter(event_type=event_type)

    search = request.GET.get('search')
    if search:
        events = events.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(location__icontains=search)
        )

    # Estadísticas
    total_events = events.count()
    published_events = events.filter(status='published').count()
    draft_events = events.filter(status='draft').count()
    upcoming_events = events.filter(start_date__gt=timezone.now()).count()

    # Paginación
    paginator = Paginator(events, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'events': page_obj,
        'total_events': total_events,
        'published_events': published_events,
        'draft_events': draft_events,
        'upcoming_events': upcoming_events,
    }

    return render(request, 'dashboard/events/event_list.html', context)


@manager_required
def event_create(request):
    """
    Crear nuevo evento.
    """
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            form.save_m2m()  # Guardar relaciones ManyToMany

            messages.success(
                request, f'Evento "{event.title}" creado exitosamente.')
            return redirect('dashboard:event_detail', pk=event.pk)
    else:
        form = EventForm()

    context = {
        'form': form,
        'title': 'Nuevo Evento',
        'action': 'Crear Evento'
    }

    return render(request, 'dashboard/events/event_form.html', context)


@manager_required
def event_detail(request, pk):
    """
    Detalle de evento.
    """
    event = get_object_or_404(Event.objects.select_related(
        'created_by').prefetch_related('categories', 'payment_methods'), pk=pk)

    # Obtener inscripciones con pagos
    registrations = event.registrations.select_related('payment').all()

    # Estadísticas
    total_registrations = registrations.count()
    accepted_registrations = registrations.filter(status='accepted').count()
    pending_registrations = registrations.filter(status='pending').count()
    waitlist_registrations = registrations.filter(status='waitlist').count()

    context = {
        'event': event,
        'registrations': registrations,
        'total_registrations': total_registrations,
        'accepted_registrations': accepted_registrations,
        'pending_registrations': pending_registrations,
        'waitlist_registrations': waitlist_registrations,
    }

    return render(request, 'dashboard/events/event_detail.html', context)


@manager_required
def event_update(request, pk):
    """
    Editar evento.
    """
    event = get_object_or_404(Event, pk=pk)

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(
                request, f'Evento "{event.title}" actualizado exitosamente.')
            return redirect('dashboard:event_detail', pk=event.pk)
    else:
        form = EventForm(instance=event)

    context = {
        'form': form,
        'event': event,
        'title': 'Editar Evento',
        'action': 'Guardar Cambios'
    }

    return render(request, 'dashboard/events/event_form.html', context)


@manager_required
def event_delete(request, pk):
    """
    Eliminar evento.
    """
    event = get_object_or_404(Event, pk=pk)

    if request.method == 'POST':
        event_title = event.title
        event.delete()
        messages.success(
            request, f'Evento "{event_title}" eliminado exitosamente.')
        return redirect('dashboard:event_list')

    context = {
        'event': event
    }

    return render(request, 'dashboard/events/event_delete.html', context)


# ===== VISTAS DE CATEGORÍAS =====

@manager_required
def category_list(request):
    """
    Lista de categorías.
    """
    categories = Category.objects.annotate(
        annotated_event_count=Count('events')).all()

    # Paginación
    paginator = Paginator(categories, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'categories': page_obj,
    }

    return render(request, 'dashboard/events/category_list.html', context)


@manager_required
def category_create(request):
    """
    Crear nueva categoría.
    """
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(
                request, f'Categoría "{category.name}" creada exitosamente.')
            return redirect('dashboard:event_category_detail', pk=category.pk)
    else:
        form = CategoryForm()

    context = {
        'form': form,
        'title': 'Nueva Categoría',
        'action': 'Crear Categoría'
    }

    return render(request, 'dashboard/events/category_form.html', context)


@manager_required
def category_detail(request, pk):
    """
    Detalle de categoría.
    """
    category = get_object_or_404(Category.objects.annotate(
        annotated_event_count=Count('events')), pk=pk)
    events = category.events.all()[:10]  # Últimos 10 eventos

    context = {
        'category': category,
        'events': events,
    }

    return render(request, 'dashboard/events/category_detail.html', context)


@manager_required
def category_update(request, pk):
    """
    Editar categoría.
    """
    category = get_object_or_404(Category, pk=pk)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(
                request, f'Categoría "{category.name}" actualizada exitosamente.')
            return redirect('dashboard:event_category_detail', pk=category.pk)
    else:
        form = CategoryForm(instance=category)

    context = {
        'form': form,
        'category': category,
        'title': 'Editar Categoría',
        'action': 'Guardar Cambios'
    }

    return render(request, 'dashboard/events/category_form.html', context)


@manager_required
def category_delete(request, pk):
    """
    Eliminar categoría.
    """
    category = get_object_or_404(Category, pk=pk)

    if request.method == 'POST':
        category_name = category.name
        category.delete()
        messages.success(
            request, f'Categoría "{category_name}" eliminada exitosamente.')
        return redirect('dashboard:event_category_list')

    context = {
        'category': category
    }

    return render(request, 'dashboard/events/category_delete.html', context)


# ===== VISTAS DE MÉTODOS DE PAGO =====

@manager_required
def payment_method_list(request):
    """
    Lista de métodos de pago.
    """
    payment_methods = PaymentMethod.objects.all()

    # Paginación
    paginator = Paginator(payment_methods, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'payment_methods': page_obj,
    }

    return render(request, 'dashboard/events/payment_method_list.html', context)


@manager_required
def payment_method_create(request):
    """
    Crear nuevo método de pago.
    """
    if request.method == 'POST':
        form = PaymentMethodForm(request.POST)
        if form.is_valid():
            payment_method = form.save()
            messages.success(
                request, f'Método de pago "{payment_method.name}" creado exitosamente.')
            return redirect('dashboard:payment_method_detail', pk=payment_method.pk)
    else:
        form = PaymentMethodForm()

    context = {
        'form': form,
        'title': 'Nuevo Método de Pago',
        'action': 'Crear Método de Pago'
    }

    return render(request, 'dashboard/events/payment_method_form.html', context)


@manager_required
def payment_method_detail(request, pk):
    """
    Detalle de método de pago.
    """
    payment_method = get_object_or_404(PaymentMethod, pk=pk)
    events = payment_method.events.all()

    context = {
        'payment_method': payment_method,
        'events': events,
    }

    return render(request, 'dashboard/events/payment_method_detail.html', context)


@manager_required
def payment_method_update(request, pk):
    """
    Editar método de pago.
    """
    payment_method = get_object_or_404(PaymentMethod, pk=pk)

    if request.method == 'POST':
        form = PaymentMethodForm(request.POST, instance=payment_method)
        if form.is_valid():
            form.save()
            messages.success(
                request, f'Método de pago "{payment_method.name}" actualizado exitosamente.')
            return redirect('dashboard:payment_method_detail', pk=payment_method.pk)
    else:
        form = PaymentMethodForm(instance=payment_method)

    context = {
        'form': form,
        'payment_method': payment_method,
        'title': 'Editar Método de Pago',
        'action': 'Guardar Cambios'
    }

    return render(request, 'dashboard/events/payment_method_form.html', context)


@manager_required
def payment_method_delete(request, pk):
    """
    Eliminar método de pago.
    """
    payment_method = get_object_or_404(PaymentMethod, pk=pk)

    if request.method == 'POST':
        payment_method_name = payment_method.name
        payment_method.delete()
        messages.success(
            request, f'Método de pago "{payment_method_name}" eliminado exitosamente.')
        return redirect('dashboard:payment_method_list')

    context = {
        'payment_method': payment_method
    }

    return render(request, 'dashboard/events/payment_method_delete.html', context)


# ===== VISTAS DE INSCRIPCIONES =====

@manager_required
def registration_list(request):
    """
    Lista de inscripciones.
    """
    registrations = Registration.objects.select_related(
        'event', 'payment').all()

    # Filtros
    status = request.GET.get('status')
    if status:
        registrations = registrations.filter(status=status)

    event_id = request.GET.get('event')
    if event_id:
        registrations = registrations.filter(event_id=event_id)

    search = request.GET.get('search')
    if search:
        registrations = registrations.filter(
            Q(full_name__icontains=search) |
            Q(email__icontains=search) |
            Q(event__title__icontains=search)
        )

    # Estadísticas
    total_registrations = registrations.count()
    pending_registrations = registrations.filter(status='pending').count()
    accepted_registrations = registrations.filter(status='accepted').count()
    waitlist_registrations = registrations.filter(status='waitlist').count()

    # Paginación
    paginator = Paginator(registrations, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'registrations': page_obj,
        'total_registrations': total_registrations,
        'pending_registrations': pending_registrations,
        'accepted_registrations': accepted_registrations,
        'waitlist_registrations': waitlist_registrations,
        'events': Event.objects.all(),  # Para filtros
    }

    return render(request, 'dashboard/events/registration_list.html', context)


@manager_required
def registration_detail(request, pk):
    """
    Detalle de inscripción.
    """
    registration = get_object_or_404(
        Registration.objects.select_related('event', 'payment'), pk=pk)

    context = {
        'registration': registration,
    }

    return render(request, 'dashboard/events/registration_detail.html', context)


@manager_required
def registration_approve(request, pk):
    """
    Aprobar inscripción.
    """
    registration = get_object_or_404(Registration, pk=pk)

    if registration.status == 'pending':
        registration.status = 'accepted'
        registration.save()

        # Enviar email de aprobación
        try:
            send_registration_approved_email(registration)
        except Exception as e:
            # Log error pero no fallar la aprobación
            print(f"Error sending approval email: {e}")

        messages.success(
            request, f'Inscripción de {registration.full_name} aprobada.')
    else:
        messages.error(
            request, 'Solo se pueden aprobar inscripciones pendientes.')

    return redirect('dashboard:registration_detail', pk=registration.pk)


@manager_required
def registration_reject(request, pk):
    """
    Rechazar inscripción.
    """
    registration = get_object_or_404(Registration, pk=pk)

    if registration.status == 'pending':
        registration.status = 'rejected'
        registration.save()

        # Enviar email de rechazo
        try:
            send_registration_rejected_email(registration)
        except Exception as e:
            # Log error pero no fallar el rechazo
            print(f"Error sending rejection email: {e}")

        messages.success(
            request, f'Inscripción de {registration.full_name} rechazada.')
    else:
        messages.error(
            request, 'Solo se pueden rechazar inscripciones pendientes.')

    return redirect('dashboard:registration_detail', pk=registration.pk)


@manager_required
def payment_verify(request, pk):
    """
    Verificar pago.
    """
    payment = get_object_or_404(Payment, pk=pk)

    if payment.status == 'pending':
        # Verificar si la inscripción estaba pendiente antes
        was_pending = payment.registration.status == 'pending'

        payment.verify_payment(request.user)

        # Si la inscripción estaba pendiente y ahora está aceptada, enviar email
        if was_pending and payment.registration.status == 'accepted':
            try:
                send_registration_approved_email(payment.registration)
            except Exception as e:
                # Log error pero no fallar la verificación
                print(
                    f"Error sending approval email after payment verification: {e}")

        messages.success(
            request, f'Pago de {payment.registration.full_name} verificado.')
    else:
        messages.error(request, 'Solo se pueden verificar pagos pendientes.')

    return redirect('dashboard:registration_detail', pk=payment.registration.pk)


# ===== VISTAS DE ESTADÍSTICAS =====

@manager_required
def event_statistics(request):
    """
    Estadísticas generales de eventos.
    """
    # Estadísticas de eventos
    total_events = Event.objects.count()
    published_events = Event.objects.filter(status='published').count()
    upcoming_events = Event.objects.filter(
        start_date__gt=timezone.now()).count()
    finished_events = Event.objects.filter(end_date__lt=timezone.now()).count()

    # Estadísticas de inscripciones
    total_registrations = Registration.objects.count()
    pending_registrations = Registration.objects.filter(
        status='pending').count()
    accepted_registrations = Registration.objects.filter(
        status='accepted').count()

    # Estadísticas de pagos
    total_payments = Payment.objects.count()
    pending_payments = Payment.objects.filter(status='pending').count()
    verified_payments = Payment.objects.filter(status='verified').count()

    # Eventos más populares
    popular_events = Event.objects.annotate(
        registration_count=Count('registrations')
    ).order_by('-registration_count')[:5]

    # Categorías más populares
    popular_categories = Category.objects.annotate(
        annotated_event_count=Count('events')
    ).order_by('-annotated_event_count')[:5]

    context = {
        'total_events': total_events,
        'published_events': published_events,
        'upcoming_events': upcoming_events,
        'finished_events': finished_events,
        'total_registrations': total_registrations,
        'pending_registrations': pending_registrations,
        'accepted_registrations': accepted_registrations,
        'total_payments': total_payments,
        'pending_payments': pending_payments,
        'verified_payments': verified_payments,
        'popular_events': popular_events,
        'popular_categories': popular_categories,
    }

    return render(request, 'dashboard/events/statistics.html', context)


# ===== VISTAS PÚBLICAS =====

def public_event_list(request):
    """
    Lista pública de eventos.
    """
    # Obtener solo eventos publicados
    events = Event.objects.filter(status='published').select_related(
        'created_by').prefetch_related('categories').all()

    # Filtros
    category_slug = request.GET.get('categoria')
    if category_slug:
        events = events.filter(categories__slug=category_slug)

    event_type = request.GET.get('tipo')
    if event_type:
        events = events.filter(event_type=event_type)

    modality = request.GET.get('modalidad')
    if modality:
        events = events.filter(modality=modality)

    search = request.GET.get('buscar')
    if search:
        events = events.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(location__icontains=search)
        )

    # Ordenar por fecha de inicio (próximos primero)
    events = events.order_by('start_date')

    # Obtener categorías para filtros
    categories = Category.objects.annotate(
        annotated_event_count=Count(
            'events', filter=Q(events__status='published'))
    ).filter(annotated_event_count__gt=0)

    # Paginación
    paginator = Paginator(events, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'events': page_obj,
        'categories': categories,
        'current_category': category_slug,
        'current_type': event_type,
        'current_modality': modality,
        'search_query': search,
    }

    return render(request, 'events/event_list.html', context)


def public_event_detail(request, slug):
    """
    Detalle público de evento.
    """
    event = get_object_or_404(
        Event.objects.select_related('created_by').prefetch_related(
            'categories', 'payment_methods'
        ).filter(status='published'),
        slug=slug
    )

    # Verificar si el usuario ya está inscrito
    user_registered = False
    if request.user.is_authenticated:
        user_registered = event.registrations.filter(
            email=request.user.email
        ).exists()

    # Obtener eventos relacionados (misma categoría)
    related_events = Event.objects.filter(
        status='published',
        categories__in=event.categories.all()
    ).exclude(pk=event.pk)[:3]

    context = {
        'event': event,
        'user_registered': user_registered,
        'related_events': related_events,
    }

    return render(request, 'events/event_detail.html', context)


def public_category_detail(request, slug):
    """
    Detalle público de categoría con sus eventos.
    """
    category = get_object_or_404(Category, slug=slug)

    events = Event.objects.filter(
        status='published',
        categories=category
    ).select_related('created_by').prefetch_related('categories').order_by('start_date')

    # Filtros adicionales
    event_type = request.GET.get('tipo')
    if event_type:
        events = events.filter(event_type=event_type)

    modality = request.GET.get('modalidad')
    if modality:
        events = events.filter(modality=modality)

    # Paginación
    paginator = Paginator(events, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'category': category,
        'events': page_obj,
        'current_type': event_type,
        'current_modality': modality,
    }

    return render(request, 'events/category_detail.html', context)


def event_registration(request, slug):
    """
    Proceso de inscripción a un evento.
    """
    event = get_object_or_404(
        Event.objects.select_related('created_by').prefetch_related(
            'payment_methods'
        ).filter(status='published'),
        slug=slug
    )

    # Verificar si el evento ya terminó
    if event.is_finished:
        messages.error(request, 'Este evento ya ha finalizado.')
        return redirect('events:event_detail', slug=slug)

    # Verificar si el usuario ya está inscrito
    if request.user.is_authenticated:
        existing_registration = event.registrations.filter(
            email=request.user.email
        ).first()
        if existing_registration:
            messages.info(request, 'Ya estás inscrito en este evento.')
            return redirect('events:event_detail', slug=slug)

    if request.method == 'POST':
        form = RegistrationForm(
            event=event, data=request.POST, files=request.FILES)
        if form.is_valid():
            registration = form.save(commit=False)
            registration.event = event

            # Determinar el estado inicial de la inscripción
            if event.is_full:
                registration.status = 'waitlist'
                messages.warning(
                    request, 'El evento está lleno. Has sido agregado a la lista de espera.')
            else:
                registration.status = 'pending'
                messages.success(
                    request, 'Tu inscripción ha sido recibida y está pendiente de aprobación.')

            registration.save()

            # Si el evento es de pago, crear el registro de pago
            if event.modality == 'paid':
                payment_method_id = request.POST.get('payment_method')
                if payment_method_id:
                    payment_method = get_object_or_404(
                        PaymentMethod, id=payment_method_id)
                    Payment.objects.create(
                        registration=registration,
                        payment_method=payment_method,
                        amount=event.price
                    )

            # Enviar email de confirmación
            try:
                send_registration_confirmation_email(registration)
            except Exception as e:
                # Log error pero no fallar la inscripción
                print(f"Error sending confirmation email: {e}")

            return redirect('events:registration_success', registration_id=registration.id)
    else:
        # Pre-llenar el formulario si el usuario está autenticado
        initial_data = {}
        if request.user.is_authenticated:
            # Obtener el nombre completo desde el perfil del usuario
            full_name = ""
            if hasattr(request.user, 'profile') and request.user.profile:
                full_name = request.user.profile.full_name

            initial_data = {
                'full_name': full_name,
                'email': request.user.email,
            }
        form = RegistrationForm(event=event, initial=initial_data)

    context = {
        'event': event,
        'form': form,
    }

    return render(request, 'events/event_registration.html', context)


def registration_success(request, registration_id):
    """
    Página de confirmación de inscripción exitosa.
    """
    registration = get_object_or_404(
        Registration.objects.select_related(
            'event', 'payment__payment_method'),
        id=registration_id
    )

    context = {
        'registration': registration,
    }

    return render(request, 'events/registration_success.html', context)


# ===== VISTAS DE GESTIÓN DE ENCUESTAS =====

@manager_required
def survey_list(request):
    """
    Lista de encuestas para el dashboard.
    """
    surveys = Survey.objects.select_related(
        'created_by').prefetch_related('questions').all()

    # Filtros
    status = request.GET.get('status')
    if status:
        surveys = surveys.filter(status=status)

    search = request.GET.get('search')
    if search:
        surveys = surveys.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search)
        )

    # Estadísticas
    total_surveys = surveys.count()
    active_surveys = surveys.filter(status='active').count()
    draft_surveys = surveys.filter(status='draft').count()

    # Paginación
    paginator = Paginator(surveys, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'surveys': page_obj,
        'total_surveys': total_surveys,
        'active_surveys': active_surveys,
        'draft_surveys': draft_surveys,
    }

    return render(request, 'dashboard/events/survey_list.html', context)


@manager_required
def survey_create(request):
    """
    Crear nueva encuesta.
    """
    if request.method == 'POST':
        form = SurveyForm(request.POST)
        if form.is_valid():
            survey = form.save(commit=False)
            survey.created_by = request.user
            survey.save()

            messages.success(
                request, f'Encuesta "{survey.title}" creada exitosamente.')
            return redirect('dashboard:survey_detail', pk=survey.pk)
    else:
        form = SurveyForm()

    context = {
        'form': form,
        'title': 'Nueva Encuesta',
        'action': 'Crear Encuesta'
    }

    return render(request, 'dashboard/events/survey_form.html', context)


@manager_required
def survey_detail(request, pk):
    """
    Detalle de encuesta.
    """
    survey = get_object_or_404(
        Survey.objects.select_related(
            'created_by').prefetch_related('questions__options'),
        pk=pk
    )

    # Estadísticas de respuestas
    total_responses = survey.responses.count()
    completed_responses = survey.responses.filter(status='completed').count()
    opened_responses = survey.responses.filter(status='opened').count()
    expired_responses = survey.responses.filter(status='expired').count()

    # Eventos que usan esta encuesta
    events_using_survey = survey.events.all()

    context = {
        'survey': survey,
        'total_responses': total_responses,
        'completed_responses': completed_responses,
        'opened_responses': opened_responses,
        'expired_responses': expired_responses,
        'events_using_survey': events_using_survey,
    }

    return render(request, 'dashboard/events/survey_detail.html', context)


@manager_required
def survey_update(request, pk):
    """
    Editar encuesta.
    """
    survey = get_object_or_404(Survey, pk=pk)

    if request.method == 'POST':
        form = SurveyForm(request.POST, instance=survey)
        if form.is_valid():
            form.save()
            messages.success(
                request, f'Encuesta "{survey.title}" actualizada exitosamente.')
            return redirect('dashboard:survey_detail', pk=survey.pk)
    else:
        form = SurveyForm(instance=survey)

    context = {
        'form': form,
        'survey': survey,
        'title': 'Editar Encuesta',
        'action': 'Guardar Cambios'
    }

    return render(request, 'dashboard/events/survey_form.html', context)


@manager_required
def survey_delete(request, pk):
    """
    Eliminar encuesta.
    """
    survey = get_object_or_404(Survey, pk=pk)

    if request.method == 'POST':
        survey_title = survey.title
        survey.delete()
        messages.success(
            request, f'Encuesta "{survey_title}" eliminada exitosamente.')
        return redirect('dashboard:survey_list')

    context = {
        'survey': survey
    }

    return render(request, 'dashboard/events/survey_delete.html', context)


@manager_required
def survey_duplicate(request, pk):
    """
    Duplicar encuesta.
    """
    survey = get_object_or_404(Survey, pk=pk)

    if request.method == 'POST':
        new_survey = survey.duplicate(request.user)
        messages.success(
            request, f'Encuesta "{survey.title}" duplicada exitosamente.')
        return redirect('dashboard:survey_detail', pk=new_survey.pk)

    context = {
        'survey': survey
    }

    return render(request, 'dashboard/events/survey_duplicate.html', context)


@manager_required
def survey_questions(request, pk):
    """
    Gestionar preguntas de una encuesta.
    """
    survey = get_object_or_404(
        Survey.objects.prefetch_related('questions__options'), pk=pk)

    if request.method == 'POST':
        formset = SurveyQuestionFormSet(request.POST, instance=survey)
        if formset.is_valid():
            formset.save()
            messages.success(
                request, f'Preguntas de la encuesta "{survey.title}" actualizadas exitosamente.')
            return redirect('dashboard:survey_detail', pk=survey.pk)
    else:
        formset = SurveyQuestionFormSet(instance=survey)

    context = {
        'survey': survey,
        'formset': formset,
    }

    return render(request, 'dashboard/events/survey_questions.html', context)


@manager_required
def question_options(request, question_pk):
    """
    Gestionar opciones de una pregunta de opciones múltiples.
    """
    question = get_object_or_404(
        SurveyQuestion.objects.select_related('survey'), pk=question_pk)

    if question.question_type != 'multiple_choice':
        messages.error(request, 'Esta pregunta no es de opciones múltiples.')
        return redirect('dashboard:survey_questions', pk=question.survey.pk)

    if request.method == 'POST':
        formset = SurveyQuestionOptionFormSet(request.POST, instance=question)
        if formset.is_valid():
            formset.save()
            messages.success(
                request, f'Opciones de la pregunta actualizadas exitosamente.')
            return redirect('dashboard:survey_questions', pk=question.survey.pk)
        else:
            # Debug: mostrar errores del formset
            for i, form in enumerate(formset.forms):
                if form.errors:
                    messages.error(
                        request, f'Errores en formulario {i}: {form.errors}')
            if formset.non_form_errors():
                messages.error(
                    request, f'Errores del formset: {formset.non_form_errors()}')
    else:
        formset = SurveyQuestionOptionFormSet(instance=question)

    context = {
        'question': question,
        'survey': question.survey,
        'formset': formset,
    }

    return render(request, 'dashboard/events/question_options.html', context)


@manager_required
def survey_results(request, pk):
    """
    Ver resultados de una encuesta.
    """
    survey = get_object_or_404(
        Survey.objects.prefetch_related(
            'questions__options', 'responses__question_responses'),
        pk=pk
    )

    # Estadísticas generales
    total_responses = survey.responses.filter(status='completed').count()

    # Análisis por pregunta
    question_analysis = []
    for question in survey.questions.all():
        responses = question.responses.filter(
            survey_response__status='completed')

        if question.question_type == 'text':
            # Para preguntas de texto, mostrar algunas respuestas de ejemplo
            text_responses = responses.exclude(text_response='')[:5]
            analysis = {
                'question': question,
                'type': 'text',
                'response_count': responses.count(),
                'sample_responses': text_responses,
            }

        elif question.question_type == 'scale':
            # Para escalas, calcular promedio y distribución
            scale_responses = responses.exclude(scale_response__isnull=True)
            if scale_responses.exists():
                avg_rating = sum(
                    r.scale_response for r in scale_responses) / scale_responses.count()
                distribution = {}
                for i in range(1, 6):
                    distribution[i] = scale_responses.filter(
                        scale_response=i).count()
            else:
                avg_rating = 0
                distribution = {i: 0 for i in range(1, 6)}

            analysis = {
                'question': question,
                'type': 'scale',
                'response_count': responses.count(),
                'average_rating': round(avg_rating, 2),
                'distribution': distribution,
            }

        elif question.question_type == 'multiple_choice':
            # Para opciones múltiples, contar cada opción
            option_counts = {}
            for option in question.options.all():
                count = option.responses.filter(
                    survey_response__status='completed').count()
                option_counts[option.text] = count

            analysis = {
                'question': question,
                'type': 'multiple_choice',
                'response_count': responses.count(),
                'option_counts': option_counts,
            }

        question_analysis.append(analysis)

    context = {
        'survey': survey,
        'total_responses': total_responses,
        'question_analysis': question_analysis,
    }

    return render(request, 'dashboard/events/survey_results.html', context)


@manager_required
def send_surveys(request, event_pk):
    """
    Enviar encuestas a los participantes de un evento.
    """
    event = get_object_or_404(
        Event.objects.select_related('survey'), pk=event_pk)

    if not event.survey:
        messages.error(request, 'Este evento no tiene una encuesta asignada.')
        return redirect('dashboard:event_detail', pk=event.pk)

    if not event.send_survey:
        messages.error(
            request, 'El envío de encuestas no está habilitado para este evento.')
        return redirect('dashboard:event_detail', pk=event.pk)

    if request.method == 'POST':
        # Crear respuestas de encuesta para participantes
        created_count = create_survey_responses_for_event(event)

        # Obtener las respuestas creadas y enviar emails
        survey_responses = SurveyResponse.objects.filter(
            survey=event.survey,
            event=event,
            status='sent'
        )

        sent_count = 0
        for survey_response in survey_responses:
            if send_survey_invitation_email(survey_response):
                sent_count += 1

        messages.success(
            request, f'Se enviaron {sent_count} encuestas exitosamente.')
        return redirect('dashboard:event_detail', pk=event.pk)

    # Mostrar vista previa de envío
    registrations_to_send = event.registrations.filter(
        status='accepted',
        survey_responses__isnull=True
    )

    already_sent = event.registrations.filter(
        status='accepted',
        survey_responses__isnull=False
    )

    context = {
        'event': event,
        'registrations_to_send': registrations_to_send,
        'already_sent': already_sent,
        'total_to_send': registrations_to_send.count(),
        'total_sent': already_sent.count(),
    }

    return render(request, 'dashboard/events/send_surveys.html', context)


# ===== VISTAS PÚBLICAS DE ENCUESTAS =====

def survey_response(request, token):
    """
    Vista pública para responder una encuesta.
    """
    survey_response_obj = get_object_or_404(
        SurveyResponse.objects.select_related(
            'survey', 'event', 'registration'),
        token=token
    )

    # Verificar si la encuesta ha expirado
    if survey_response_obj.is_expired:
        messages.error(request, 'Esta encuesta ha expirado.')
        return redirect('events:survey_expired')

    # Verificar si ya fue completada
    if survey_response_obj.status == 'completed':
        messages.info(request, 'Ya has completado esta encuesta.')
        return redirect('events:survey_thanks')

    # Marcar como abierta
    survey_response_obj.mark_opened()

    if request.method == 'POST':
        form = SurveyResponseForm(survey_response_obj, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Gracias por completar la encuesta!')
            return redirect('events:survey_thanks')
    else:
        form = SurveyResponseForm(survey_response_obj)

    context = {
        'survey_response': survey_response_obj,
        'survey': survey_response_obj.survey,
        'event': survey_response_obj.event,
        'form': form,
    }

    return render(request, 'events/survey_response.html', context)


def survey_thanks(request):
    """
    Página de agradecimiento después de completar la encuesta.
    """
    return render(request, 'events/survey_thanks.html')


def survey_expired(request):
    """
    Página para encuestas expiradas.
    """
    return render(request, 'events/survey_expired.html')
