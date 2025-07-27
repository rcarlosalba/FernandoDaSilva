from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from django.utils import timezone
from datetime import timedelta


def send_email_notification(email_type, registration, context=None):
    """
    Función genérica para enviar diferentes tipos de notificaciones por email.

    Args:
        email_type (str): Tipo de email ('registration_confirmation', 'registration_approved', 'event_reminder')
        registration (Registration): Objeto de inscripción
        context (dict): Contexto adicional para el template

    Returns:
        bool: True si el email fue enviado exitosamente, False en caso contrario
    """
    if context is None:
        context = {}

    # Configuraciones de email
    email_configs = {
        'registration_confirmation': {
            'subject': f'Confirmación de Inscripción - {registration.event.title}',
            'template': 'events/emails/registration_confirmation.html',
        },
        'registration_approved': {
            'subject': f'¡Inscripción Aprobada! - {registration.event.title}',
            'template': 'events/emails/registration_approved.html',
        },
        'registration_rejected': {
            'subject': f'Inscripción No Aprobada - {registration.event.title}',
            'template': 'events/emails/registration_rejected.html',
        },
        'event_reminder': {
            'subject': f'Recordatorio: {registration.event.title} - Mañana',
            'template': 'events/emails/event_reminder.html',
        }
    }

    config = email_configs.get(email_type)
    if not config:
        raise ValueError(f"Email type '{email_type}' not supported")

    # Agregar contexto común
    context.update({
        'registration': registration,
        'event': registration.event,
        'site_name': 'Fernando Da Silva',
        'recipient_email': registration.email,
    })

    try:
        # Renderizar contenido del email
        html_message = render_to_string(config['template'], context)
        plain_message = strip_tags(html_message)

        # Enviar email
        send_mail(
            subject=config['subject'],
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[registration.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True

    except Exception as e:
        # Log error en producción
        print(f"Error sending email: {e}")
        return False


def send_registration_confirmation_email(registration):
    """
    Envía email de confirmación de recepción de inscripción.
    """
    return send_email_notification(
        email_type='registration_confirmation',
        registration=registration
    )


def send_registration_approved_email(registration):
    """
    Envía email de notificación de aprobación de inscripción.
    """
    return send_email_notification(
        email_type='registration_approved',
        registration=registration
    )


def send_registration_rejected_email(registration):
    """
    Envía email de notificación de rechazo de inscripción.
    """
    return send_email_notification(
        email_type='registration_rejected',
        registration=registration
    )


def send_event_reminder_email(registration):
    """
    Envía email de recordatorio 24 horas antes del evento.
    """
    return send_email_notification(
        email_type='event_reminder',
        registration=registration
    )


def send_waitlist_notification_email(registration):
    """
    Envía email de notificación cuando se libera un cupo para alguien en lista de espera.
    """
    context = {
        'cupo_liberado': True,
    }
    return send_email_notification(
        email_type='registration_approved',
        registration=registration,
        context=context
    )


def schedule_event_reminders():
    """
    Programa recordatorios para eventos que están a 24 horas de comenzar.
    Esta función puede ser llamada por un cron job o task scheduler.
    """
    from .models import Registration

    tomorrow = timezone.now() + timedelta(days=1)
    start_of_tomorrow = tomorrow.replace(
        hour=0, minute=0, second=0, microsecond=0)
    end_of_tomorrow = start_of_tomorrow + timedelta(days=1)

    # Obtener inscripciones aprobadas para eventos que comienzan mañana
    registrations = Registration.objects.filter(
        status='accepted',
        event__start_date__gte=start_of_tomorrow,
        event__start_date__lt=end_of_tomorrow
    ).select_related('event')

    for registration in registrations:
        send_event_reminder_email(registration)

    return len(registrations)


# ====== FUNCIONES DE ENCUESTAS ======

def send_survey_invitation_email(survey_response):
    """
    Envía email de invitación para completar la encuesta de satisfacción.
    """
    try:
        # Construir el enlace de la encuesta
        survey_url = f"{settings.SITE_URL}/eventos/encuesta/{survey_response.token}/"

        # Contexto para el template
        context = {
            'survey_response': survey_response,
            'survey': survey_response.survey,
            'event': survey_response.event,
            'registration': survey_response.registration,
            'survey_url': survey_url,
            'expires_at': survey_response.expires_at,
            'site_name': 'Fernando Da Silva',
        }

        # Renderizar contenido del email
        html_message = render_to_string(
            'events/emails/survey_invitation.html', context)
        plain_message = strip_tags(html_message)

        # Enviar email
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
        print(
            f"Error enviando encuesta a {survey_response.registration.email}: {e}")
        return False


def send_survey_reminder_email(survey_response):
    """
    Envía email de recordatorio para completar la encuesta.
    """
    try:
        # Construir el enlace de la encuesta
        survey_url = f"{settings.SITE_URL}/eventos/encuesta/{survey_response.token}/"

        # Contexto para el template
        context = {
            'survey_response': survey_response,
            'survey': survey_response.survey,
            'event': survey_response.event,
            'registration': survey_response.registration,
            'survey_url': survey_url,
            'expires_at': survey_response.expires_at,
            'site_name': 'Fernando Da Silva',
        }

        # Renderizar contenido del email
        html_message = render_to_string(
            'events/emails/survey_reminder.html', context)
        plain_message = strip_tags(html_message)

        # Enviar email
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
        print(
            f"Error enviando recordatorio a {survey_response.registration.email}: {e}")
        return False


def create_survey_responses_for_event(event):
    """
    Crea respuestas de encuesta para todos los participantes de un evento.
    """
    from .models import SurveyResponse

    if not event.survey or not event.send_survey:
        return 0

    # Obtener inscripciones aceptadas que no tienen respuesta de encuesta
    registrations = event.registrations.filter(
        status='accepted',
        survey_responses__isnull=True
    )

    created_count = 0
    for registration in registrations:
        # Crear respuesta de encuesta
        survey_response = SurveyResponse.objects.create(
            survey=event.survey,
            event=event,
            registration=registration
        )
        created_count += 1

    return created_count


def send_surveys_for_event_manual(event):
    """
    Envía encuestas para un evento específico de forma manual.
    """
    from .models import SurveyResponse

    if not event.survey or not event.send_survey:
        return 0

    # Obtener respuestas de encuesta no enviadas
    survey_responses = SurveyResponse.objects.filter(
        survey=event.survey,
        event=event,
        status='sent'
    )

    sent_count = 0
    for survey_response in survey_responses:
        if send_survey_invitation_email(survey_response):
            sent_count += 1

    return sent_count


def cleanup_expired_survey_responses():
    """
    Marca como expiradas las encuestas que han superado su tiempo límite.
    """
    from .models import SurveyResponse

    expired_responses = SurveyResponse.objects.filter(
        status__in=['sent', 'opened'],
        expires_at__lt=timezone.now()
    )

    for response in expired_responses:
        response.status = 'expired'
        response.save()

    return expired_responses.count()
