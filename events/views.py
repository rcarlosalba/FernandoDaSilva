from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from .models import Event, Category, PaymentMethod, Registration, Payment, SurveyResponse
from .forms import RegistrationForm, SurveyResponseForm
from .utils import send_registration_confirmation_email

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
