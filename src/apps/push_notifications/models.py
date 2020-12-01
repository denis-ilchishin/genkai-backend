from django.conf import settings
from django.db import models
from django.db.models import JSONField
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from apps.core.models import BaseModel


class PushNotificationSubscription(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_query_name='push_notification_subscription',
        related_name='push_notification_subscriptions',
    )
    subscription = JSONField(_('Обьект подписки'))
    device = models.CharField(_('Устройство'), max_length=255, null=True, blank=True)
    date_subscribed = models.DateTimeField(default=now)
