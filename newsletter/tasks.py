from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.urls import reverse
from django.conf import settings
from .models import Newsletter, Subscriber
import logging

logger = logging.getLogger(__name__)


def send_newsletter_task(newsletter_id):
    """
    Asynchronous task to send newsletter to all active subscribers.
    This task is designed to be executed by Django-Q.
    """
    logger.info(f"Starting newsletter task for newsletter_id: {newsletter_id}")

    try:
        # Get the newsletter
        newsletter = Newsletter.objects.get(id=newsletter_id)
        logger.info(f"Found newsletter: {newsletter.title}")

        # Verify newsletter is in sending status
        if newsletter.status != 'sending':
            logger.error(
                f"Newsletter {newsletter_id} is not in sending status")
            return False

        # Get all active subscribers
        subscribers = Subscriber.objects.filter(
            is_subscribed=True).select_related('user')
        subscriber_count = subscribers.count()

        if subscriber_count == 0:
            logger.warning(
                f"No active subscribers found for newsletter {newsletter_id}")
            newsletter.status = 'sent'
            newsletter.sent_date = timezone.now()
            newsletter.save()
            return True

        logger.info(
            f"Starting to send newsletter '{newsletter.title}' to {subscriber_count} subscribers")

        sent_count = 0
        failed_count = 0

        # Send email to each subscriber
        for subscriber in subscribers:
            try:
                success = send_newsletter_email(newsletter, subscriber)
                if success:
                    sent_count += 1
                else:
                    failed_count += 1

            except Exception as e:
                logger.error(
                    f"Failed to send newsletter to {subscriber.user.email}: {str(e)}")
                failed_count += 1

        # Update newsletter status
        newsletter.status = 'sent'
        newsletter.sent_date = timezone.now()
        newsletter.save()

        logger.info(
            f"Newsletter '{newsletter.title}' sending completed. Sent: {sent_count}, Failed: {failed_count}")

        return True

    except Newsletter.DoesNotExist:
        logger.error(f"Newsletter with id {newsletter_id} does not exist")
        return False

    except Exception as e:
        logger.error(
            f"Unexpected error sending newsletter {newsletter_id}: {str(e)}")

        # Reset newsletter status to draft on failure
        try:
            newsletter = Newsletter.objects.get(id=newsletter_id)
            newsletter.status = 'draft'
            newsletter.save()
        except:
            pass

        return False


def send_newsletter_email(newsletter, subscriber):
    """
    Send individual newsletter email to a subscriber.

    Args:
        newsletter: Newsletter instance
        subscriber: Subscriber instance

    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        # Generate unsubscribe URL
        unsubscribe_url = f"{settings.SITE_URL}{reverse('newsletter:unsubscribe', kwargs={'token': subscriber.unsubscribe_token})}"

        # Prepare context for email template
        context = {
            'newsletter': newsletter,
            'user': subscriber.user,
            'subscriber': subscriber,
            'unsubscribe_url': unsubscribe_url,
            'preview_mode': False,
        }

        # Render email content
        html_content = render_to_string(
            'dashboard/newsletter/emails/newsletter.html', context)

        # Create email message
        subject = newsletter.title
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [subscriber.user.email]

        # Create email with HTML content
        email = EmailMultiAlternatives(
            subject=subject,
            body="Please enable HTML to view this email.",  # Fallback text
            from_email=from_email,
            to=to_email
        )

        email.attach_alternative(html_content, "text/html")

        # Send email
        email.send()

        logger.debug(
            f"Newsletter sent successfully to {subscriber.user.email}")
        return True

    except Exception as e:
        logger.error(
            f"Failed to send newsletter email to {subscriber.user.email}: {str(e)}")
        return False


def send_test_newsletter(newsletter_id, test_email):
    """
    Send a test newsletter to a specific email address.

    Args:
        newsletter_id: Newsletter ID
        test_email: Email address to send test to

    Returns:
        bool: True if test email was sent successfully, False otherwise
    """
    try:
        newsletter = Newsletter.objects.get(id=newsletter_id)

        # Generate dummy unsubscribe URL for test
        unsubscribe_url = f"{settings.SITE_URL}#test-unsubscribe"

        # Prepare context for email template
        context = {
            'newsletter': newsletter,
            'user': {'email': test_email, 'first_name': 'Test', 'last_name': 'User'},
            'unsubscribe_url': unsubscribe_url,
            'preview_mode': False,
        }

        # Render email content
        html_content = render_to_string(
            'dashboard/newsletter/emails/newsletter.html', context)

        # Create email message
        subject = f"[TEST] {newsletter.title}"
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [test_email]

        # Create email with HTML content
        email = EmailMultiAlternatives(
            subject=subject,
            body="Please enable HTML to view this email.",  # Fallback text
            from_email=from_email,
            to=to_email
        )

        email.attach_alternative(html_content, "text/html")

        # Send email
        email.send()

        logger.info(f"Test newsletter sent successfully to {test_email}")
        return True

    except Newsletter.DoesNotExist:
        logger.error(f"Newsletter with id {newsletter_id} does not exist")
        return False

    except Exception as e:
        logger.error(
            f"Failed to send test newsletter to {test_email}: {str(e)}")
        return False
