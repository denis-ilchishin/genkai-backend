from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from apps.notifications.models import Notification
from apps.push_notifications.tasks import send_push_notification_task
from apps.users.models import User

from .models import Episode, Update


@receiver(
    m2m_changed,
    sender=Update.added_episodes.through,
    dispatch_uid='update_added_episodes_signal',
)
def update_added_episodes_signal(action, pk_set, **kwargs):
    if action == 'post_add':
        notifications = []
        for episode in Episode.objects.filter(pk__in=pk_set):
            users_to_notify = User.objects.filter(
                subscription__translator=episode.translation.translator,
                subscription__title=episode.translation.title,
            )
            for user in users_to_notify:
                notifications.append(
                    Notification(
                        user=user,
                        type=Notification.TYPES.subscription,
                        episode=episode,
                    )
                )
        Notification.objects.bulk_create(notifications)

        for notification in notifications:
            send_push_notification_task.delay(notification.id)
