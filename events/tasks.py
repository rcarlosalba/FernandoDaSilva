"""
Tareas asíncronas para el sistema de notificaciones de eventos.

Este módulo contiene todas las tareas que se ejecutan en segundo plano
para enviar emails transaccionales relacionados con eventos.
"""

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from django_q.tasks import async_task
from .models import Registration, Event


def send_registration_confirmation(registration_id):
    """
    Envía email de confirmación de recepción de inscripción.

    Args:
        registration_id (int): ID de la inscripción
    """
    try:
        registration = Registration.objects.select_related(
            'event').get(id=registration_id)

        context = {
            'registration': registration,
            'event': registration.event,
            'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
        }

        subject = f'Confirmación de inscripción - {registration.event.title}'
        html_message = render_to_string(
            'events/emails/registration_confirmation.html', context)
        plain_message = render_to_string(
            'events/emails/registration_confirmation.txt', context)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[registration.email],
            html_message=html_message,
            fail_silently=False,
        )

        return f"Email de confirmación enviado a {registration.email}"

    except Registration.DoesNotExist:
        return f"Error: Inscripción {registration_id} no encontrada"
    except Exception as e:
        return f"Error enviando email de confirmación: {str(e)}"


def send_registration_accepted(registration_id):
    """
    Envía email de confirmación de inscripción aceptada.

    Args:
        registration_id (int): ID de la inscripción
    """
    try:
        registration = Registration.objects.select_related(
            'event').get(id=registration_id)

        context = {
            'registration': registration,
            'event': registration.event,
            'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
        }

        subject = f'¡Inscripción aceptada! - {registration.event.title}'
        html_message = render_to_string(
            'events/emails/registration_accepted.html', context)
        plain_message = render_to_string(
            'events/emails/registration_accepted.txt', context)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[registration.email],
            html_message=html_message,
            fail_silently=False,
        )

        return f"Email de aceptación enviado a {registration.email}"

    except Registration.DoesNotExist:
        return f"Error: Inscripción {registration_id} no encontrada"
    except Exception as e:
        return f"Error enviando email de aceptación: {str(e)}"


def send_payment_instructions(registration_id):
    """
    Envía email con instrucciones de pago para eventos de pago.

    Args:
        registration_id (int): ID de la inscripción
    """
    try:
        registration = Registration.objects.select_related(
            'event', 'payment__payment_method'
        ).get(id=registration_id)

        if not hasattr(registration, 'payment'):
            return f"Error: Inscripción {registration_id} no tiene pago asociado"

        context = {
            'registration': registration,
            'event': registration.event,
            'payment': registration.payment,
            'payment_method': registration.payment.payment_method,
            'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
        }

        subject = f'Instrucciones de pago - {registration.event.title}'
        html_message = render_to_string(
            'events/emails/payment_instructions.html', context)
        plain_message = render_to_string(
            'events/emails/payment_instructions.txt', context)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[registration.email],
            html_message=html_message,
            fail_silently=False,
        )

        return f"Email de instrucciones de pago enviado a {registration.email}"

    except Registration.DoesNotExist:
        return f"Error: Inscripción {registration_id} no encontrada"
    except Exception as e:
        return f"Error enviando email de instrucciones de pago: {str(e)}"


def send_event_reminder(registration_id):
    """
    Envía email de recordatorio antes del evento.

    Args:
        registration_id (int): ID de la inscripción
    """
    try:
        registration = Registration.objects.select_related(
            'event').get(id=registration_id)

        # Solo enviar si la inscripción está aceptada
        if registration.status != 'accepted':
            return f"Inscripción {registration_id} no está aceptada"

        context = {
            'registration': registration,
            'event': registration.event,
            'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
        }

        subject = f'Recordatorio: {registration.event.title}'
        html_message = render_to_string(
            'events/emails/event_reminder.html', context)
        plain_message = render_to_string(
            'events/emails/event_reminder.txt', context)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[registration.email],
            html_message=html_message,
            fail_silently=False,
        )

        return f"Email de recordatorio enviado a {registration.email}"

    except Registration.DoesNotExist:
        return f"Error: Inscripción {registration_id} no encontrada"
    except Exception as e:
        return f"Error enviando email de recordatorio: {str(e)}"


def send_satisfaction_survey(registration_id):
    """
    Envía email con enlace a la encuesta de satisfacción.

    Args:
        registration_id (int): ID de la inscripción
    """
    try:
        registration = Registration.objects.select_related(
            'event').get(id=registration_id)

        # Solo enviar si la inscripción está aceptada
        if registration.status != 'accepted':
            return f"Inscripción {registration_id} no está aceptada"

        context = {
            'registration': registration,
            'event': registration.event,
            'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
        }

        subject = f'Encuesta de satisfacción - {registration.event.title}'
        html_message = render_to_string(
            'events/emails/satisfaction_survey.html', context)
        plain_message = render_to_string(
            'events/emails/satisfaction_survey.txt', context)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[registration.email],
            html_message=html_message,
            fail_silently=False,
        )

        return f"Email de encuesta enviado a {registration.email}"

    except Registration.DoesNotExist:
        return f"Error: Inscripción {registration_id} no encontrada"
    except Exception as e:
        return f"Error enviando email de encuesta: {str(e)}"


def send_registration_rejected(registration_id):
    """
    Envía email de notificación de inscripción rechazada.

    Args:
        registration_id (int): ID de la inscripción
    """
    try:
        registration = Registration.objects.select_related(
            'event').get(id=registration_id)

        context = {
            'registration': registration,
            'event': registration.event,
            'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
        }

        subject = f'Inscripción no aprobada - {registration.event.title}'
        html_message = render_to_string(
            'events/emails/registration_rejected.html', context)
        plain_message = render_to_string(
            'events/emails/registration_rejected.txt', context)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[registration.email],
            html_message=html_message,
            fail_silently=False,
        )

        return f"Email de rechazo enviado a {registration.email}"

    except Registration.DoesNotExist:
        return f"Error: Inscripción {registration_id} no encontrada"
    except Exception as e:
        return f"Error enviando email de rechazo: {str(e)}"


def send_event_cancelled(registration_id):
    """
    Envía email de notificación de evento cancelado.

    Args:
        registration_id (int): ID de la inscripción
    """
    try:
        registration = Registration.objects.select_related(
            'event').get(id=registration_id)

        context = {
            'registration': registration,
            'event': registration.event,
            'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
        }

        subject = f'Evento cancelado - {registration.event.title}'
        html_message = render_to_string(
            'events/emails/event_cancelled.html', context)
        plain_message = render_to_string(
            'events/emails/event_cancelled.txt', context)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[registration.email],
            html_message=html_message,
            fail_silently=False,
        )

        return f"Email de cancelación enviado a {registration.email}"

    except Registration.DoesNotExist:
        return f"Error: Inscripción {registration_id} no encontrada"
    except Exception as e:
        return f"Error enviando email de cancelación: {str(e)}"


# Funciones helper para programar tareas
def schedule_registration_confirmation(registration_id):
    """Programa el envío de confirmación de inscripción."""
    return async_task(send_registration_confirmation, registration_id)


def schedule_registration_accepted(registration_id):
    """Programa el envío de confirmación de inscripción aceptada."""
    return async_task(send_registration_accepted, registration_id)


def schedule_payment_instructions(registration_id):
    """Programa el envío de instrucciones de pago."""
    return async_task(send_payment_instructions, registration_id)


def schedule_event_reminder(registration_id, reminder_hours=24):
    """
    Programa el envío de recordatorio del evento.

    Args:
        registration_id (int): ID de la inscripción
        reminder_hours (int): Horas antes del evento para enviar el recordatorio
    """
    from django_q.tasks import schedule

    registration = Registration.objects.get(id=registration_id)
    reminder_time = registration.event.start_date - \
        timezone.timedelta(hours=reminder_hours)

    # Solo programar si el recordatorio es en el futuro
    if reminder_time > timezone.now():
        return schedule(
            'events.tasks.send_event_reminder',
            registration_id,
            schedule_type='O',  # One time
            next_run=reminder_time
        )

    return None


def schedule_satisfaction_survey(registration_id, survey_hours=24):
    """
    Programa el envío de encuesta de satisfacción.

    Args:
        registration_id (int): ID de la inscripción
        survey_hours (int): Horas después del evento para enviar la encuesta
    """
    from django_q.tasks import schedule

    registration = Registration.objects.get(id=registration_id)
    survey_time = registration.event.end_date + \
        timezone.timedelta(hours=survey_hours)

    return schedule(
        'events.tasks.send_satisfaction_survey',
        registration_id,
        schedule_type='O',  # One time
        next_run=survey_time
    )


def schedule_registration_rejected(registration_id):
    """Programa el envío de notificación de inscripción rechazada."""
    return async_task(send_registration_rejected, registration_id)


def schedule_event_cancelled(registration_id):
    """Programa el envío de notificación de evento cancelado."""
    return async_task(send_event_cancelled, registration_id)
