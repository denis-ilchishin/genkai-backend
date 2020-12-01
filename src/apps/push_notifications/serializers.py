from rest_framework import serializers

from . import models


class PushNotificationSubscriptionObjectSerializer(serializers.Serializer):
    endpoint = serializers.URLField()
    keys = serializers.DictField()
    expirationTime = serializers.CharField(required=False, allow_null=True)


class PushNotificationSubscriptionSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    subscription = PushNotificationSubscriptionObjectSerializer()
    device = serializers.CharField(required=False, max_length=255)

    class Meta:
        model = models.PushNotificationSubscription
        fields = ('subscription', 'device', 'user')
