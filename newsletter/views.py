from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from django_q.tasks import async_task
from constants.constant import manager_required
from .models import Newsletter, Subscriber
from .forms import NewsletterForm, NewsletterSearchForm
from .tasks import send_newsletter_task


@manager_required
def newsletter_list(request):
    """
    List all newsletters with search and filter functionality.
    """
    newsletters = Newsletter.objects.all()
    form = NewsletterSearchForm(request.GET or None)

    if form.is_valid():
        search = form.cleaned_data.get('search')
        status = form.cleaned_data.get('status')

        if search:
            newsletters = newsletters.filter(
                Q(title__icontains=search) | Q(content__icontains=search)
            )

        if status:
            newsletters = newsletters.filter(status=status)

    context = {
        'newsletters': newsletters,
        'form': form,
        'total_subscribers': Subscriber.objects.filter(is_subscribed=True).count(),
    }
    return render(request, 'dashboard/newsletter/list.html', context)


@manager_required
def newsletter_create(request):
    """
    Create a new newsletter.
    """
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            newsletter = form.save()
            messages.success(
                request, f'Newsletter "{newsletter.title}" creado exitosamente.')
            return redirect('newsletter:list')
    else:
        form = NewsletterForm()

    context = {
        'form': form,
        'title': 'Crear Newsletter',
        'action': 'Crear'
    }
    return render(request, 'dashboard/newsletter/form.html', context)


@manager_required
def newsletter_edit(request, pk):
    """
    Edit an existing newsletter.
    """
    newsletter = get_object_or_404(Newsletter, pk=pk)

    if not newsletter.can_edit():
        messages.error(request, 'Este newsletter no puede ser editado.')
        return redirect('newsletter:list')

    if request.method == 'POST':
        form = NewsletterForm(request.POST, instance=newsletter)
        if form.is_valid():
            newsletter = form.save()
            messages.success(
                request, f'Newsletter "{newsletter.title}" actualizado exitosamente.')
            return redirect('newsletter:list')
    else:
        form = NewsletterForm(instance=newsletter)

    context = {
        'form': form,
        'newsletter': newsletter,
        'title': 'Editar Newsletter',
        'action': 'Actualizar'
    }
    return render(request, 'dashboard/newsletter/form.html', context)


@manager_required
def newsletter_delete(request, pk):
    """
    Delete a newsletter.
    """
    newsletter = get_object_or_404(Newsletter, pk=pk)

    if not newsletter.can_delete():
        messages.error(request, 'Este newsletter no puede ser eliminado.')
        return redirect('newsletter:list')

    if request.method == 'POST':
        title = newsletter.title
        newsletter.delete()
        messages.success(
            request, f'Newsletter "{title}" eliminado exitosamente.')
        return redirect('newsletter:list')

    context = {
        'newsletter': newsletter,
        'title': 'Eliminar Newsletter'
    }
    return render(request, 'dashboard/newsletter/delete.html', context)


@manager_required
def newsletter_preview(request, pk):
    """
    Preview a newsletter.
    """
    newsletter = get_object_or_404(Newsletter, pk=pk)

    context = {
        'newsletter': newsletter,
        'preview_mode': True,
        'unsubscribe_url': '#'  # Placeholder for preview
    }
    return render(request, 'dashboard/newsletter/emails/newsletter.html', context)


@manager_required
def newsletter_send(request, pk):
    """
    Send a newsletter (enqueue for asynchronous sending).
    """
    newsletter = get_object_or_404(Newsletter, pk=pk)

    if not newsletter.can_send():
        messages.error(request, 'Este newsletter no puede ser enviado.')
        return redirect('newsletter:list')

    if request.method == 'POST':
        # Update status to sending
        newsletter.status = 'sending'
        newsletter.save()

        # Enqueue asynchronous task
        try:
            async_task('newsletter.tasks.send_newsletter_task',
                       newsletter_id=newsletter.id)
        except ImportError:
            # Fallback: send synchronously if Django-Q is not available
            send_newsletter_task(newsletter.id)

        messages.success(
            request, f'Newsletter "{newsletter.title}" está siendo enviado. Se te notificará cuando se complete.')
        return redirect('newsletter:list')

    subscriber_count = Subscriber.objects.filter(is_subscribed=True).count()

    context = {
        'newsletter': newsletter,
        'subscriber_count': subscriber_count,
        'title': 'Enviar Newsletter'
    }
    return render(request, 'dashboard/newsletter/send.html', context)


def unsubscribe(request, token):
    """
    Unsubscribe a user using their token.
    """
    try:
        subscriber = Subscriber.objects.get(unsubscribe_token=token)

        if request.method == 'POST':
            subscriber.unsubscribe()
            messages.success(
                request, 'Has sido desuscribido exitosamente de nuestro newsletter.')
            return redirect('newsletter:unsubscribe_success')

        context = {
            'subscriber': subscriber,
            'user': subscriber.user
        }
        return render(request, 'newsletter/unsubscribe.html', context)

    except Subscriber.DoesNotExist:
        messages.error(request, 'Enlace de desuscripción inválido.')
        return redirect('public:index')


def unsubscribe_success(request):
    """
    Show unsubscribe success message.
    """
    return render(request, 'newsletter/unsubscribe_success.html')


def resubscribe(request, token):
    """
    Resubscribe a user using their token.
    """
    try:
        subscriber = Subscriber.objects.get(unsubscribe_token=token)

        if request.method == 'POST':
            subscriber.resubscribe()
            messages.success(
                request, 'You have been successfully resubscribed to our newsletter.')
            return redirect('newsletter:resubscribe_success')

        context = {
            'subscriber': subscriber,
            'user': subscriber.user
        }
        return render(request, 'newsletter/resubscribe.html', context)

    except Subscriber.DoesNotExist:
        messages.error(request, 'Invalid resubscribe link.')
        return redirect('public:index')


def resubscribe_success(request):
    """
    Show resubscribe success message.
    """
    return render(request, 'newsletter/resubscribe_success.html')
