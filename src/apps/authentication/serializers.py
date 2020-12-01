from rest_framework import serializers
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer as BaseTokenObtainPairSerializer,
)

from apps.core.serializers import CaptchaSerializerMixin
from apps.users.models import User


class SocialMediaSerializer(CaptchaSerializerMixin, serializers.Serializer):
    data = serializers.DictField(required=True)


class TokenObtainPairSerializer(BaseTokenObtainPairSerializer):
    username_field = User.EMAIL_FIELD

