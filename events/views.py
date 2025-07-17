from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from django.utils import timezone
from constants.constant import manager_required
from .models import Event, Category, PaymentMethod, Registration, Payment
from .forms import EventForm, CategoryForm, PaymentMethodForm, RegistrationForm, PaymentForm


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

    # Ordenar por fecha de inicio (más recientes primero)
    events = events.order_by('-start_date')

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


@manager_required
def event_cancel(request, pk):
    """
    Cancelar evento.
    """
    event = get_object_or_404(Event, pk=pk)

    if request.method == 'POST':
        from .services import EventService
        if EventService.cancel_event(event, request.user):
            messages.success(request, 'Evento cancelado exitosamente.')
        else:
            messages.error(request, 'Error al cancelar el evento.')
        return redirect('dashboard:event_list')

    context = {
        'event': event,
    }
    return render(request, 'dashboard/events/event_cancel.html', context)


# ===== VISTAS DE CATEGORÍAS =====

@manager_required
def category_list(request):
    """
    Lista de categorías.
    """
    categories = Category.objects.annotate(
        annotated_event_count=Count('events')).order_by('name')

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
    payment_methods = PaymentMethod.objects.order_by('name')

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
    registrations = registrations.order_by('-registration_date')
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
        from .services import RegistrationService
        if RegistrationService.accept_registration(registration, request.user):
            messages.success(
                request, f'Inscripción de {registration.full_name} aprobada.')
        else:
            messages.error(
                request, 'Error al aprobar la inscripción.')
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
        from .services import RegistrationService
        if RegistrationService.reject_registration(registration, request.user):
            messages.success(
                request, f'Inscripción de {registration.full_name} rechazada.')
        else:
            messages.error(
                request, 'Error al rechazar la inscripción.')
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
        from .services import PaymentService
        if PaymentService.verify_payment(payment, request.user):
            messages.success(
                request, f'Pago de {payment.registration.full_name} verificado.')
        else:
            messages.error(
                request, 'Error al verificar el pago.')
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
        form = RegistrationForm(request.POST, request.FILES)
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

            # Enviar email de confirmación usando el servicio
            from .services import NotificationService
            NotificationService.send_registration_confirmation(registration)

            return redirect('events:registration_success', registration_id=registration.id)
    else:
        # Pre-llenar el formulario si el usuario está autenticado
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'full_name': f"{request.user.first_name} {request.user.last_name}".strip(),
                'email': request.user.email,
            }
        form = RegistrationForm(initial=initial_data)

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
