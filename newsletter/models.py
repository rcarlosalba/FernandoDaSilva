import secrets
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from constants.constant import NEWSLETTER_STATUS_CHOICES

User = get_user_model()


class Newsletter(models.Model):
    """
    Represents an email campaign/newsletter.
    """

    title = models.CharField(max_length=200, verbose_name='Title')
    content = models.TextField(verbose_name='Content (HTML)')
    status = models.CharField(
        max_length=10,
        choices=NEWSLETTER_STATUS_CHOICES,
        default='draft',
        verbose_name='Status'
    )
    sent_date = models.DateTimeField(
        null=True, blank=True, verbose_name='Sent Date')
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Newsletter'
        verbose_name_plural = 'Newsletters'

    def __str__(self):
        return self.title

    def can_edit(self):
        """Returns True if the newsletter can be edited."""
        return self.status == 'draft'

    def can_send(self):
        """Returns True if the newsletter can be sent."""
        return self.status == 'draft'

    def can_delete(self):
        """Returns True if the newsletter can be deleted."""
        return self.status == 'draft'


class Subscriber(models.Model):
    """
    Represents a user's subscription to newsletters.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='newsletter_subscription',
        verbose_name='User'
    )
    is_subscribed = models.BooleanField(
        default=True, verbose_name='Is Subscribed')
    unsubscribe_token = models.CharField(
        max_length=64,
        unique=True,
        verbose_name='Unsubscribe Token'
    )
    subscribed_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Subscribed At')
    unsubscribed_at = models.DateTimeField(
        null=True, blank=True, verbose_name='Unsubscribed At')

    class Meta:
        verbose_name = 'Subscriber'
        verbose_name_plural = 'Subscribers'

    def __str__(self):
        return f"{self.user.email} - {'Subscribed' if self.is_subscribed else 'Unsubscribed'}"

    def save(self, *args, **kwargs):
        """Generate unsubscribe token if not present."""
        if not self.unsubscribe_token:
            self.unsubscribe_token = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)

    def unsubscribe(self):
        """Unsubscribe the user."""
        self.is_subscribed = False
        self.unsubscribed_at = timezone.now()
        self.save()

    def resubscribe(self):
        """Resubscribe the user."""
        self.is_subscribed = True
        self.unsubscribed_at = None
        self.save()
