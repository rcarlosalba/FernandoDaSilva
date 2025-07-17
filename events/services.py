"""
Servicios para el manejo de notificaciones de eventos.

Este módulo contiene la lógica de negocio para el envío de emails
y la gestión de notificaciones relacionadas con eventos.
"""

from django.db import transaction
from .models import Registration, Event, Payment
from .tasks import (
    schedule_registration_confirmation,
    schedule_registration_accepted,
    schedule_payment_instructions,
    schedule_event_reminder,
    schedule_satisfaction_survey,
    schedule_registration_rejected,
    schedule_event_cancelled
)


class NotificationService:
    """
    Servicio para manejar todas las notificaciones relacionadas con eventos.
    """

    @staticmethod
    def send_registration_confirmation(registration):
        """
        Envía email de confirmación de inscripción.

        Args:
            registration (Registration): Instancia de inscripción
        """
        try:
            schedule_registration_confirmation(registration.id)
            return True
        except Exception as e:
            print(f"Error enviando confirmación de inscripción: {e}")
            return False

    @staticmethod
    def send_registration_accepted(registration):
        """
        Envía email de confirmación de inscripción aceptada.

        Args:
            registration (Registration): Instancia de inscripción
        """
        try:
            schedule_registration_accepted(registration.id)

            # Programar recordatorio del evento
            schedule_event_reminder(registration.id)

            # Si el evento tiene encuesta habilitada, programar envío
            if registration.event.send_survey:
                schedule_satisfaction_survey(registration.id)

            return True
        except Exception as e:
            print(f"Error enviando aceptación de inscripción: {e}")
            return False

    @staticmethod
    def send_payment_instructions(registration):
        """
        Envía email con instrucciones de pago.

        Args:
            registration (Registration): Instancia de inscripción
        """
        try:
            if registration.event.modality == 'paid' and hasattr(registration, 'payment'):
                schedule_payment_instructions(registration.id)
                return True
            return False
        except Exception as e:
            print(f"Error enviando instrucciones de pago: {e}")
            return False

    @staticmethod
    def send_registration_rejected(registration):
        """
        Envía email de notificación de inscripción rechazada.

        Args:
            registration (Registration): Instancia de inscripción
        """
        try:
            schedule_registration_rejected(registration.id)
            return True
        except Exception as e:
            print(f"Error enviando rechazo de inscripción: {e}")
            return False

    @staticmethod
    def send_event_cancelled_notifications(event):
        """
        Envía notificaciones de cancelación a todos los inscritos.

        Args:
            event (Event): Instancia del evento cancelado
        """
        try:
            registrations = event.registrations.filter(status='accepted')
            for registration in registrations:
                schedule_event_cancelled(registration.id)
            return True
        except Exception as e:
            print(f"Error enviando notificaciones de cancelación: {e}")
            return False


class RegistrationService:
    """
    Servicio para manejar la lógica de inscripciones.
    """

    @staticmethod
    def create_registration(event, full_name, email, phone, notes=''):
        """
        Crea una nueva inscripción y envía notificaciones correspondientes.

        Args:
            event (Event): Evento al que se inscribe
            full_name (str): Nombre completo del participante
            email (str): Email del participante
            phone (str): Teléfono del participante
            notes (str): Notas adicionales

        Returns:
            Registration: Instancia de inscripción creada
        """
        with transaction.atomic():
            # Determinar el estado inicial
            if event.is_full:
                status = 'waitlist'
            else:
                status = 'pending'

            # Crear la inscripción
            registration = Registration.objects.create(
                event=event,
                full_name=full_name,
                email=email,
                phone=phone,
                status=status,
                notes=notes
            )

            # Enviar email de confirmación
            NotificationService.send_registration_confirmation(registration)

            return registration

    @staticmethod
    def accept_registration(registration, user=None):
        """
        Acepta una inscripción y envía notificaciones correspondientes.

        Args:
            registration (Registration): Instancia de inscripción
            user (User): Usuario que acepta la inscripción

        Returns:
            bool: True si se aceptó correctamente
        """
        try:
            with transaction.atomic():
                registration.status = 'accepted'
                registration.save()

                # Enviar notificación de aceptación
                NotificationService.send_registration_accepted(registration)

                return True
        except Exception as e:
            print(f"Error aceptando inscripción: {e}")
            return False

    @staticmethod
    def reject_registration(registration, user=None):
        """
        Rechaza una inscripción y envía notificaciones correspondientes.

        Args:
            registration (Registration): Instancia de inscripción
            user (User): Usuario que rechaza la inscripción

        Returns:
            bool: True si se rechazó correctamente
        """
        try:
            with transaction.atomic():
                registration.status = 'rejected'
                registration.save()

                # Enviar notificación de rechazo
                NotificationService.send_registration_rejected(registration)

                # Si hay lista de espera, notificar al siguiente
                if registration.event.registrations.filter(status='waitlist').exists():
                    next_waitlist = registration.event.registrations.filter(
                        status='waitlist'
                    ).first()
                    if next_waitlist:
                        next_waitlist.status = 'pending'
                        next_waitlist.save()
                        NotificationService.send_registration_confirmation(
                            next_waitlist)

                return True
        except Exception as e:
            print(f"Error rechazando inscripción: {e}")
            return False


class PaymentService:
    """
    Servicio para manejar la lógica de pagos.
    """

    @staticmethod
    def create_payment(registration, payment_method, receipt=None):
        """
        Crea un registro de pago y envía notificaciones correspondientes.

        Args:
            registration (Registration): Instancia de inscripción
            payment_method (PaymentMethod): Método de pago seleccionado
            receipt (File): Comprobante de pago (opcional)

        Returns:
            Payment: Instancia de pago creada
        """
        try:
            with transaction.atomic():
                payment = Payment.objects.create(
                    registration=registration,
                    payment_method=payment_method,
                    amount=registration.event.price,
                    receipt=receipt
                )

                # Enviar instrucciones de pago
                NotificationService.send_payment_instructions(registration)

                return payment
        except Exception as e:
            print(f"Error creando pago: {e}")
            return None

    @staticmethod
    def verify_payment(payment, user):
        """
        Verifica un pago y actualiza el estado de la inscripción.

        Args:
            payment (Payment): Instancia de pago
            user (User): Usuario que verifica el pago

        Returns:
            bool: True si se verificó correctamente
        """
        try:
            with transaction.atomic():
                payment.verify_payment(user)

                # Enviar notificación de aceptación
                NotificationService.send_registration_accepted(
                    payment.registration)

                return True
        except Exception as e:
            print(f"Error verificando pago: {e}")
            return False


class EventService:
    """
    Servicio para manejar la lógica de eventos.
    """

    @staticmethod
    def cancel_event(event, user=None):
        """
        Cancela un evento y envía notificaciones a todos los inscritos.

        Args:
            event (Event): Instancia del evento
            user (User): Usuario que cancela el evento

        Returns:
            bool: True si se canceló correctamente
        """
        try:
            with transaction.atomic():
                event.status = 'cancelled'
                event.save()

                # Enviar notificaciones de cancelación
                NotificationService.send_event_cancelled_notifications(event)

                return True
        except Exception as e:
            print(f"Error cancelando evento: {e}")
            return False

    @staticmethod
    def finish_event(event):
        """
        Marca un evento como finalizado y programa encuestas si corresponde.

        Args:
            event (Event): Instancia del evento

        Returns:
            bool: True si se finalizó correctamente
        """
        try:
            with transaction.atomic():
                event.status = 'finished'
                event.save()

                # Si el evento tiene encuesta habilitada, programar envío
                if event.send_survey:
                    accepted_registrations = event.registrations.filter(
                        status='accepted')
                    for registration in accepted_registrations:
                        schedule_satisfaction_survey(registration.id)

                return True
        except Exception as e:
            print(f"Error finalizando evento: {e}")
            return False
