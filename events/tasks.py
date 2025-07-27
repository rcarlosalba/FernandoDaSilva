"""
Tareas programadas para el sistema de encuestas.
"""
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django_q.tasks import async_task, schedule
from django_q.models import Schedule

from .models import SurveyResponse, Event


def send_survey_email(survey_response):
    """
    Envía un email con el enlace de la encuesta.
    """
    try:
        # Construir el enlace de la encuesta
        survey_url = f"{settings.SITE_URL}/eventos/encuesta/{survey_response.token}/"

        # Renderizar el template del email
        context = {
            'survey_response': survey_response,
            'survey': survey_response.survey,
            'event': survey_response.event,
            'registration': survey_response.registration,
            'survey_url': survey_url,
            'expires_at': survey_response.expires_at,
        }

        html_message = render_to_string(
            'events/emails/survey_invitation.html', context)
        plain_message = render_to_string(
            'events/emails/survey_invitation.txt', context)

        # Enviar el email
        send_mail(
            subject=f'Encuesta de satisfacción - {survey_response.event.title}',
            message=plain_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[survey_response.registration.email],
            fail_silently=False,
        )

        # Marcar como enviada
        survey_response.status = 'sent'
        survey_response.save()

        return True

    except Exception as e:
        # Log del error
        print(
            f"Error enviando encuesta a {survey_response.registration.email}: {str(e)}")
        return False


def send_survey_reminder(survey_response):
    """
    Envía un recordatorio para completar la encuesta.
    """
    try:
        # Construir el enlace de la encuesta
        survey_url = f"{settings.SITE_URL}/eventos/encuesta/{survey_response.token}/"

        # Renderizar el template del email
        context = {
            'survey_response': survey_response,
            'survey': survey_response.survey,
            'event': survey_response.event,
            'registration': survey_response.registration,
            'survey_url': survey_url,
            'expires_at': survey_response.expires_at,
        }

        html_message = render_to_string(
            'events/emails/survey_reminder.html', context)
        plain_message = render_to_string(
            'events/emails/survey_reminder.txt', context)

        # Enviar el email
        send_mail(
            subject=f'Recordatorio: Encuesta de satisfacción - {survey_response.event.title}',
            message=plain_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[survey_response.registration.email],
            fail_silently=False,
        )

        return True

    except Exception as e:
        # Log del error
        print(
            f"Error enviando recordatorio a {survey_response.registration.email}: {str(e)}")
        return False


def send_surveys_for_event(event_id):
    """
    Envía encuestas para todos los participantes de un evento.
    """
    try:
        event = Event.objects.get(id=event_id)

        if not event.survey or not event.send_survey:
            return False

        # Obtener inscripciones aceptadas que no tienen respuesta de encuesta
        registrations = event.registrations.filter(
            status='accepted',
            survey_responses__isnull=True
        )

        sent_count = 0
        for registration in registrations:
            # Crear respuesta de encuesta
            survey_response = SurveyResponse.objects.create(
                survey=event.survey,
                event=event,
                registration=registration
            )

            # Enviar email de forma asíncrona
            async_task(send_survey_email, survey_response)
            sent_count += 1

        return sent_count

    except Event.DoesNotExist:
        return False
    except Exception as e:
        print(f"Error enviando encuestas para evento {event_id}: {str(e)}")
        return False


def schedule_survey_reminders():
    """
    Programa recordatorios para encuestas no completadas.
    """
    # Obtener respuestas enviadas pero no completadas que no han expirado
    pending_responses = SurveyResponse.objects.filter(
        status='sent',
        expires_at__gt=timezone.now(),
        completed_at__isnull=True
    )

    for response in pending_responses:
        # Calcular cuándo enviar el recordatorio (24 horas después del envío)
        reminder_time = response.sent_at + timezone.timedelta(hours=24)

        # Solo programar si aún no ha pasado el tiempo del recordatorio
        if reminder_time > timezone.now():
            # Verificar si ya existe un recordatorio programado
            existing_schedule = Schedule.objects.filter(
                func='events.tasks.send_survey_reminder',
                args=f'[{response.id}]'
            ).first()

            if not existing_schedule:
                schedule(
                    'events.tasks.send_survey_reminder',
                    response.id,
                    schedule_type=Schedule.ONCE,
                    next_run=reminder_time
                )


def cleanup_expired_surveys():
    """
    Marca como expiradas las encuestas que han superado su tiempo límite.
    """
    expired_responses = SurveyResponse.objects.filter(
        status__in=['sent', 'opened'],
        expires_at__lt=timezone.now()
    )

    for response in expired_responses:
        response.status = 'expired'
        response.save()

    return expired_responses.count()


def send_bulk_surveys_task(event_ids):
    """
    Tarea para enviar encuestas a múltiples eventos de forma asíncrona.
    """
    results = {}

    for event_id in event_ids:
        try:
            sent_count = send_surveys_for_event(event_id)
            results[event_id] = {
                'success': True,
                'sent_count': sent_count
            }
        except Exception as e:
            results[event_id] = {
                'success': False,
                'error': str(e)
            }

    return results
