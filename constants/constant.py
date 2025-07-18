"""
Constants for the FDS project.

This module is intended to store all the global or application-wide constants
to avoid hardcoding values ("magic strings" or "magic numbers") directly in the code.
Using constants improves readability, maintainability, and reduces the risk of errors
caused by typos in literal values.

Convention:
- All constants must be in UPPER_SNAKE_CASE.
- Group related constants together with a descriptive comment if necessary.
"""

from functools import wraps
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib.auth.decorators import user_passes_test

# User Roles
# These roles define the access levels and capabilities of users within the system.
# The roles are hierarchical in terms of permissions, from the least privileged (Subscriber)
# to the most privileged (Manager).


class UserRoles:
    """
    Defines the roles for users in the system.
    """
    SUBSCRIBER = 'subscriber'
    MEMBER = 'member'
    STUDENT = 'student'
    ASSISTANT = 'assistant'
    MANAGER = 'manager'

    CHOICES = (
        (SUBSCRIBER, 'Subscriber'),
        (MEMBER, 'Member'),
        (STUDENT, 'Student'),
        (ASSISTANT, 'Assistant'),
        (MANAGER, 'Manager'),
    )

    @classmethod
    def get_choices(cls):
        """
        Returns the choices tuple for model fields.
        """
        return cls.CHOICES

    @classmethod
    def get_default(cls):
        """
        Returns the default role for a new user.
        """
        return cls.SUBSCRIBER


# Decorators
# These decorators provide role-based access control for views.
# They ensure that only users with appropriate roles can access certain functionality.


def manager_required(view_func):
    """
    Decorator that checks if the user has manager role.
    Redirects to home page if user doesn't have manager role.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')

        if request.user.role != UserRoles.MANAGER:
            return redirect('public:index')

        return view_func(request, *args, **kwargs)

    return wrapper


def manager_required_class(view_class):
    """
    Class decorator that checks if the user has manager role.
    For use with class-based views.
    """

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')

        if request.user.role != UserRoles.MANAGER:
            return redirect('public:index')

        return super(view_class, self).dispatch(request, *args, **kwargs)

    view_class.dispatch = dispatch
    return view_class


# Newsletter Status
NEWSLETTER_STATUS_CHOICES = [
    ('draft', 'Borrador'),
    ('sending', 'Enviando'),
    ('sent', 'Enviado'),
]

# Event Status
EVENT_STATUS_CHOICES = [
    ('draft', 'Borrador'),
    ('published', 'Publicado'),
    ('finished', 'Finalizado'),
    ('cancelled', 'Cancelado'),
]

# Event Type
EVENT_TYPE_CHOICES = [
    ('presential', 'Presencial'),
    ('online', 'Online'),
]

# Event Modality
EVENT_MODALITY_CHOICES = [
    ('free', 'Gratis'),
    ('paid', 'De Pago'),
]

# Payment Method Type
PAYMENT_METHOD_TYPE_CHOICES = [
    ('transfer', 'Transferencia'),
    ('cash', 'Efectivo'),
    ('external_link', 'Enlace Externo'),
]

# Registration Status
REGISTRATION_STATUS_CHOICES = [
    ('pending', 'Pendiente de Aprobación'),
    ('accepted', 'Aceptada'),
    ('rejected', 'Rechazada'),
    ('waitlist', 'En Lista de Espera'),
]

# Payment Status
PAYMENT_STATUS_CHOICES = [
    ('pending', 'Pendiente'),
    ('verified', 'Verificado'),
    ('failed', 'Fallido'),
]

# Survey Question Types
SURVEY_QUESTION_TYPE_CHOICES = [
    ('text', 'Texto libre'),
    ('scale', 'Escala (1-5)'),
    ('multiple_choice', 'Opciones múltiples'),
]

# Survey Status
SURVEY_STATUS_CHOICES = [
    ('draft', 'Borrador'),
    ('active', 'Activa'),
    ('inactive', 'Inactiva'),
]

# Survey Response Status
SURVEY_RESPONSE_STATUS_CHOICES = [
    ('sent', 'Enviada'),
    ('opened', 'Abierta'),
    ('completed', 'Completada'),
    ('expired', 'Expirada'),
]
