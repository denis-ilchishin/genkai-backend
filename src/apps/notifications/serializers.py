from django.conf import settings
from rest_framework import fields, serializers

from apps.notifications.models import Notification
from apps.titles.serializers import BaseTitleSerializer
from apps.translations.models import Episode
from apps.translations.serializers import TranslatorSerializer

from . import models

# class SubscriptionNotificationSerializer(serializers.Serializer):
#     id = serializers.IntegerField()
#     translator = TranslatorSerializer(source='episode.translation.translator')
#     title = BaseTitleSerializer(source='episode.translation.title')
#     episode = serializers.SerializerMethodField()

#     def get_episode(self, notification: models.Notification):
#         return notification.episode.number or notification.episode.title


class SubscriptionNotificationSerializer(serializers.ModelSerializer):
    translator = TranslatorSerializer(source='translation.translator')
    title = BaseTitleSerializer(source='translation.title')
    episode = serializers.SerializerMethodField()

    class Meta:
        model = Episode
        fields = ('id', 'title', 'translator', 'episode')

    def get_episode(self, episode: Episode):
        return episode.number or episode.title


class NotificationSerializer(serializers.ModelSerializer):
    related = serializers.SerializerMethodField()

    class Meta:
        model = models.Notification
        fields = ('id', 'user', 'seen', 'type', 'related', 'date_created')

    def get_related(self, notification: models.Notification):

        if notification.type == notification.TYPES.subscription:
            return SubscriptionNotificationSerializer(notification.episode).data


class NotificationIdsSerializer(serializers.Serializer):
    ids = serializers.ListField(
        child=serializers.IntegerField(min_value=0),
        allow_empty=False,
        max_length=settings.NOTIFICATIONS_MAX_NUMBER_SELECTED,
    )
