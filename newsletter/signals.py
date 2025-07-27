from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from constants.constant import UserRoles
from .models import Subscriber

User = get_user_model()


@receiver(post_save, sender=User)
def create_subscriber(sender, instance, created, **kwargs):
    """
    Create a Subscriber instance when a new User is created
    with SUBSCRIBER or MEMBER role.
    """
    if created and instance.role in [UserRoles.SUBSCRIBER, UserRoles.MEMBER]:
        Subscriber.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_subscriber(sender, instance, **kwargs):
    """
    Ensure subscriber exists for users with SUBSCRIBER or MEMBER role.
    """
    if instance.role in [UserRoles.SUBSCRIBER, UserRoles.MEMBER]:
        if not hasattr(instance, 'newsletter_subscription'):
            Subscriber.objects.create(user=instance)