from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.mixins import DateCreatedMixin
from apps.core.models import BaseModel

from . import exceptions


class Notification(BaseModel, DateCreatedMixin):
    """
    Notification model. Used to display notifications on frontend
    side and send push notification to users' browsers
    """

    class TYPES(models.IntegerChoices):
        subscription = 1, _('подписка')
        # comment = 'comment', _('ответ на комментарий')
        # site = 'site', _('сайт')

    PUSH_NOTIFICATION_TEXT = {
        TYPES.subscription: _('%(title)s - Добавлен %(episode)s-й эпизод')
    }

    PUSH_NOTIFICATION_URLS = {TYPES.subscription: '/title/%(slug)s/'}

    TYPE_RELATED_ATTRIBUTES = {
        TYPES.subscription: 'episode',
    }

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications'
    )
    type = models.PositiveSmallIntegerField(choices=TYPES.choices)
    seen = models.BooleanField(default=False)
    episode = models.ForeignKey(
        'translations.Episode', null=True, on_delete=models.CASCADE, blank=True
    )

    class Meta:
        ordering = ('-date_created',)

    def save(self, *args, **kwargs):
        # Due to the `multicolon pattern`, we need to perform some check before saving
        self._check_type()
        self._check_type_related_attributes()

        super().save(*args, **kwargs)

    def _check_type_related_attributes(self):
        attributes = self.TYPE_RELATED_ATTRIBUTES
        for _type in self.TYPES:
            if not getattr(self, attributes[_type], None):
                raise exceptions.NotificationRelatedInvalid()
            elif (related := getattr(self, attributes[_type], None)) and not related.id:
                raise exceptions.NotificationRelatedNotSaved()

    def _check_type(self):
        if not self.type:
            raise exceptions.NotificationInvalidType()

    def _get_push_notification_text_context(self):
        if self.type == self.TYPES.subscription:
            return dict(
                title=self.episode.translation.title.name, episode=self.episode.number
            )

    def _get_push_notification_url_context(self):
        if self.type == self.TYPES.subscription:
            return dict(slug=self.episode.translation.title.slug)

    def get_push_notification_text(self) -> str:
        """Get push notification text

        Raises:
            NotificationInvalidType: If `type` attribute in not the one of `TYPES`

        Returns:
            str: notification text
        """
        if self.type in self.TYPES:
            return (
                self.PUSH_NOTIFICATION_TEXT[self.type]
                % self._get_push_notification_text_context()
            )
        else:
            raise exceptions.NotificationInvalidType()

    def get_push_notification_url(self) -> str:
        """Get push notification relative URL
        This value must be synchronized with frontend app
       

        Raises:
            NotificationInvalidType: If `type` attribute is not the one of `TYPES`

        Returns:
            str: frontend app relative URL
        """
        if self.type in self.TYPES:
            return (
                self.PUSH_NOTIFICATION_URLS[self.type]
                % self._get_push_notification_url_context()
            )
        else:
            raise exceptions.NotificationInvalidType()
