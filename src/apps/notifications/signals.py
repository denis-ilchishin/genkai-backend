from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.push_notifications.tasks import send_push_notification_task

from .models import Notification


@receiver(post_save, sender=Notification, dispatch_uid='create_notification_signal')
def create_notification_signal(created, instance, **kwargs):
    if created:
        send_push_notification_task.delay(instance.id)
