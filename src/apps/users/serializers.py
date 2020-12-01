import logging

from django.contrib.auth.password_validation import validate_password
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.settings import api_settings

from apps.core import services
from apps.core.serializers import CaptchaSerializerMixin
from apps.titles.models import Title
from apps.titles.serializers import (
    BaseTitleSerializer,
    BaseTitleSerializerMeta,
    EpisodeSerializer,
    TitleSerializer,
)
from apps.translations.serializers import TranslatorSerializer
from apps.users.models import User

from . import models

logger = logging.getLogger(__name__)


class UserSubscriptionTitleSerializer(BaseTitleSerializer):
    class Meta(BaseTitleSerializerMeta):
        fields = BaseTitleSerializerMeta.fields + ('status',)


class UserSubscriptionCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    title = serializers.SlugRelatedField('slug', queryset=Title.objects.enabled())

    class Meta:
        model = models.UserSubscription
        fields = (
            'translator',
            'title',
            'user',
        )


class UserSubscriptionRetrieveSerializer(serializers.ModelSerializer):
    translator = TranslatorSerializer()
    title = UserSubscriptionTitleSerializer()

    class Meta:
        model = models.UserSubscription
        fields = ('id', 'translator', 'title', 'date_created')


class UserListTitleTitleSerializer(BaseTitleSerializer):
    class Meta(BaseTitleSerializerMeta):
        fields = BaseTitleSerializerMeta.fields + ('status', 'year', 'type')


class UserListTitleSerializer(serializers.ModelSerializer):
    title = serializers.SlugRelatedField('slug', queryset=Title.objects.enabled())

    class Meta:
        model = models.UserListTitle
        fields = ('id', 'list', 'title')

    def to_representation(self, instance):
        self.fields['title'] = UserListTitleTitleSerializer()
        return super().to_representation(instance)


class UserListSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    list_titles = serializers.SerializerMethodField()

    class Meta:
        model = models.UserList
        fields = ('id', 'user', 'list_titles', 'name')

    def get_list_titles(self, user_list: models.UserList):
        return UserListTitleSerializer(
            user_list.titles.through.objects.filter(list=user_list), many=True
        ).data


class UserBaseSerializerMeta:
    model = User
    fields = ('id', 'username', 'profile')


class UserProfileSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = models.UserProfile
        fields = ('birthday', 'sex', 'about_myself', 'image')

    def get_image(self, user):
        return user.image.urls


class UserBaseSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()

    class Meta(UserBaseSerializerMeta):
        pass


class PublicUserSerializer(UserBaseSerializer):
    """
    Serialization for private user data, must be avaliable only for current user
    """

    class Meta(UserBaseSerializerMeta):
        pass
        # fields = UserBaseSerializerMeta.fields + []


class PrivateUserSerailizer(UserBaseSerializer):
    """
    Serialization for private user data, must be avaliable only for current user
    """

    lists = serializers.SerializerMethodField()
    subscriptions = serializers.SerializerMethodField()
    notifications_count = serializers.IntegerField(
        source='get_not_seen_notifications_count'
    )

    class Meta(UserBaseSerializerMeta):
        fields = UserBaseSerializerMeta.fields + (
            'date_modified',
            'date_created',
            'last_login',
            'email',
            'lists',
            'subscriptions',
            'notifications_count',
            'date_created',
        )

    def get_lists(self, user: User):
        return UserListSerializer(user.get_lists(), many=True).data

    def get_subscriptions(self, user: User):
        return UserSubscriptionRetrieveSerializer(
            user.get_subscriptions(), many=True
        ).data


class LastViewedTitleSerializer(serializers.ModelSerializer):
    episode = EpisodeSerializer()
    title = TitleSerializer(source='episode.translation.title')
    translator = TranslatorSerializer(source='episode.translation.translator')

    class Meta:
        model = models.ViewedEpisode
        fields = ('episode', 'title', 'translator')


class ViewedEpisodeSerializer(CaptchaSerializerMixin, serializers.ModelSerializer):
    class CurrentUserDefault:
        requires_context = True

        def __call__(self, serializer_field):
            user = serializer_field.context['request'].user
            return user if user.is_authenticated else None

        def __repr__(self):
            return '%s()' % self.__class__.__name__

    user = serializers.HiddenField(default=CurrentUserDefault())
    translation = serializers.IntegerField(
        source='episode.translation.pk', read_only=True
    )
    start_from = serializers.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(32767)]
    )

    class Meta:
        model = models.ViewedEpisode
        fields = ('user', 'episode', 'translation', 'start_from', 'captcha')


class TitleRatingSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    title = serializers.SlugRelatedField('slug', queryset=Title.objects.enabled())

    class Meta:
        model = models.TitleRating
        fields = ('user', 'title', 'rate')

    def get_unique_together_validators(self):
        """
        Overriding method to disable unique together checks.
        We do that to provide `toggle` effect.
        !!! So we have to check whether the rate already exists to prevent 
            throwing database unique together exception. !!!
        """
        return []


USERNAME_FIELD = User._meta.get_field('username')
EMAIL_FIELD = User._meta.get_field('email')
PASSWORD_FIELD = User._meta.get_field('password')


class UserRegisterSerializer(CaptchaSerializerMixin, serializers.Serializer):

    email = serializers.EmailField()
    username = serializers.CharField(
        validators=USERNAME_FIELD.validators, max_length=USERNAME_FIELD.max_length
    )
    password = serializers.CharField(
        max_length=PASSWORD_FIELD.max_length, validators=[validate_password]
    )
    password_confirmation = serializers.CharField()

    def validate(self, attrs):

        email = attrs.get('email')
        username = attrs.get('username')
        password = attrs.get('password')
        password_confirmation = attrs.get('password_confirmation')

        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError(
                {
                    api_settings.NON_FIELD_ERRORS_KEY: _(
                        'Данный адрес почтовый почты недоступен'
                    )
                }
            )

        if User.objects.filter(username=username).exists():
            raise ValidationError(
                {api_settings.NON_FIELD_ERRORS_KEY: _('Данный никнейм недоступен')}
            )

        if password_confirmation != password:
            raise ValidationError(
                {api_settings.NON_FIELD_ERRORS_KEY: _('Пароль не совпадает')}
            )

        return super().validate(attrs)
