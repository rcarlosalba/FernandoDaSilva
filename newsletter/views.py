from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Subscriber


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
