from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from django.urls import reverse
from django.core.signing import Signer, TimestampSigner


def send_email_notification(email_type, recipient_email, context=None, request=None):
    """
    Generic function to send different types of email notifications.

    Args:
        email_type (str): Type of email ('welcome_subscriber', 'welcome_member', 
                         'account_deactivation', 'password_reset')
        recipient_email (str): Email address of the recipient
        context (dict): Additional context for the email template
        request (HttpRequest): Request object for building absolute URIs

    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    if context is None:
        context = {}

    # Email configurations
    email_configs = {
        'welcome_subscriber': {
            'subject': 'Bienvenido a Fernando Da Silva - Completa tu perfil',
            'template': 'accounts/emails/welcome_subscriber.html',
            'requires_signed_url': True,
        },
        'welcome_member': {
            'subject': 'Bienvenido como miembro - Fernando Da Silva',
            'template': 'accounts/emails/welcome_member.html',
            'requires_signed_url': False,
        },
        'account_deactivation': {
            'subject': 'Cuenta desactivada - Fernando Da Silva',
            'template': 'accounts/emails/account_deactivation.html',
            'requires_signed_url': False,
        },
        'password_reset': {
            'subject': 'Recuperación de contraseña - Fernando Da Silva',
            'template': 'accounts/emails/password_reset.html',
            'requires_signed_url': True,
        }
    }

    config = email_configs.get(email_type)
    if not config:
        raise ValueError(f"Email type '{email_type}' not supported")

    # Generate signed URL if required
    if config['requires_signed_url'] and 'user_id' in context and request:
        if email_type == 'password_reset':
            # Use TimestampSigner for password reset (expires in 3 hours)
            signer = TimestampSigner()
        else:
            # Use regular Signer for other types
            signer = Signer()
        
        signed_user_id = signer.sign(context['user_id'])

        if email_type == 'welcome_subscriber':
            url_path = reverse('accounts:complete_profile',
                               kwargs={'signed_user_id': signed_user_id})
        elif email_type == 'password_reset':
            url_path = reverse('accounts:password_reset_confirm',
                               kwargs={'signed_user_id': signed_user_id})

        context['action_url'] = request.build_absolute_uri(url_path)

    # Add common context
    context.update({
        'site_name': 'Fernando Da Silva',
        'recipient_email': recipient_email,
    })

    try:
        # Render email content
        html_message = render_to_string(config['template'], context)
        plain_message = strip_tags(html_message)

        # Send email
        send_mail(
            subject=config['subject'],
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            html_message=html_message,
            fail_silently=False,
        )
        return True

    except Exception as e:
        # Log error in production
        print(f"Error sending email: {e}")
        return False


def send_welcome_subscriber_email(recipient_email, user_id, request):
    """
    Convenience function for sending welcome subscriber email.
    """
    return send_email_notification(
        email_type='welcome_subscriber',
        recipient_email=recipient_email,
        context={'user_id': user_id},
        request=request
    )


def send_welcome_member_email(recipient_email):
    """
    Convenience function for sending welcome member email.
    """
    return send_email_notification(
        email_type='welcome_member',
        recipient_email=recipient_email
    )


def send_account_deactivation_email(recipient_email):
    """
    Convenience function for sending account deactivation email.
    """
    return send_email_notification(
        email_type='account_deactivation',
        recipient_email=recipient_email
    )


def send_password_reset_email(recipient_email, user_id, request):
    """
    Convenience function for sending password reset email with timestamp token.
    """
    return send_email_notification(
        email_type='password_reset',
        recipient_email=recipient_email,
        context={'user_id': user_id},
        request=request
    )
