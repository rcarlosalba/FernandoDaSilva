from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings


def send_welcome_assignment_email(assignment, manager_email=None):
    """
    Envía un correo de bienvenida al estudiante asignado a un programa.
    El manager que realiza la asignación recibirá una copia oculta (BCC).
    """
    student = assignment.student
    program = assignment.program
    to_email = student.email
    student_name = getattr(student, 'get_full_name', lambda: str(student))()
    program_title = getattr(program, 'title', str(program))

    # Renderizar el cuerpo del correo
    html_content = render_to_string(
        'programs/emails/welcome_assignment.html',
        {
            'student_name': student_name,
            'program_title': program_title,
        }
    )

    subject = f"¡Bienvenido a tu programa: {program_title}!"
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL',
                         None) or 'no-reply@fds.com'

    # Determinar el email del manager para BCC
    bcc = []
    if manager_email:
        bcc.append(manager_email)
    elif hasattr(assignment, 'assigned_by') and getattr(assignment.assigned_by, 'email', None):
        bcc.append(assignment.assigned_by.email)

    email = EmailMessage(
        subject=subject,
        body=html_content,
        from_email=from_email,
        to=[to_email],
        bcc=bcc,
    )
    email.content_subtype = 'html'  # Enviar como HTML
    try:
        email.send(fail_silently=False)
        return True
    except Exception as e:
        # Aquí podrías loggear el error si lo deseas
        return False
