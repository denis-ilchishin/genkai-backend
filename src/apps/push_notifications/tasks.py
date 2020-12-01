from __future__ import absolute_import, unicode_literals

from celery import shared_task

from apps.notifications.models import Notification

from .services import send_push_notification


@shared_task
def send_push_notification_task(notification_id):
    send_push_notification(Notification.objects.get_or_none(pk=notification_id))
