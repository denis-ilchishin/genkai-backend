from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.contrib.auth.models import UserManager as BaseUserManager
from django.contrib.auth.models import send_mail
from django.contrib.auth.validators import validators
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models
from django.db.models import QuerySet
from django.db.models.expressions import F
from django.utils.translation import gettext_lazy as _

from apps.core.fields import BaseImageField
from apps.core.mixins import DateCreatedMixin, DateCreatedModifiedMixin
from apps.core.models import BaseModel
from apps.core.query import BaseManager
from apps.titles.query import filter_queryset_by_enabled_title

from . import storages, validators


class UserManager(BaseManager, BaseUserManager):
    def _create_user(self, username, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def _create_user_via_social_media(self, username, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not username:
            raise ValueError('The given username must be set')
        username = self.model.normalize_username(username)
        user = self.model(username=username, **extra_fields)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_user_via_social_media(self, username, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user_via_social_media(username, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, BaseModel, DateCreatedModifiedMixin):

    username = models.CharField(
        _('username'),
        max_length=settings.USERS_USERNAME_MAX_LENGTH,
        unique=True,
        help_text=_(
            'Required. From %s to %s characters. Letters, digits and @/./+/-/_ only.'
        )
        % (settings.USERS_USERNAME_MIN_LENGTH, settings.USERS_USERNAME_MAX_LENGTH),
        validators=[
            validators.UnicodeUsernameValidator(),
            MinLengthValidator(settings.USERS_USERNAME_MIN_LENGTH),
            MaxLengthValidator(settings.USERS_USERNAME_MAX_LENGTH),
        ],
        error_messages={'unique': _("A user with that username already exists."),},
    )
    email = models.EmailField(_('email address'), blank=False, unique=True, null=True,)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    telegram_id = models.PositiveIntegerField(
        _('Telegram ID'), null=True, editable=False, unique=True,
    )
    vk_id = models.PositiveIntegerField(
        _('VK ID'), null=True, editable=False, unique=True,
    )

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def get_lists(self) -> QuerySet:
        return self.lists.all()

    def get_public_lists(self) -> QuerySet:
        return self.lists.filter(is_public=True)

    def get_subscriptions(self) -> QuerySet:
        return self.subscriptions.enabled()

    def get_notifications(self) -> QuerySet:
        return self.notifications.enabled()

    def get_not_seen_notifications_count(self) -> int:
        return self.get_notifications().filter(seen=False).count()


class UserProfile(BaseModel):
    class SEX(models.TextChoices):
        male = 'male', _('мужской')
        female = 'female', _('женский')
        other = 'other', _('другой')
        animeshnik = 'animeshnik', _('анимешник')

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        primary_key=True,
        on_delete=models.CASCADE,
        related_name='profile',
        related_query_name='profile',
    )
    image = BaseImageField(
        _('avatar'),
        storage=storages.UserImageStorage(),
        upload_to=storages.user_image_path,
        null=True,
        blank=True,
    )
    birthday = models.DateField(_('дата рождения'), null=True, blank=True)
    sex = models.CharField(
        _('пол'), max_length=30, choices=SEX.choices, null=True, blank=True
    )
    about_myself = models.CharField(
        _('о себе'),
        max_length=settings.USERS_PROFILE_ABOUTMYSELF_MAX_LENGTH,
        default='',
        blank=True,
    )

    class Meta:
        verbose_name = _('Профиль')

    def __str__(self):
        return getattr(self.user, self.user.USERNAME_FIELD)


class UserSubscriptionManager(BaseManager):
    def enabled(self):
        return filter_queryset_by_enabled_title(super().enabled(), 'title')


class UserSubscription(BaseModel, DateCreatedMixin):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        related_query_name='subscription',
    )
    title = models.ForeignKey('titles.Title', on_delete=models.CASCADE)
    translator = models.ForeignKey('translations.Translator', on_delete=models.CASCADE)

    class Meta:
        unique_together = (('user', 'title', 'translator'),)


class UserListTitle(BaseModel):
    list = models.ForeignKey('UserList', on_delete=models.CASCADE)
    title = models.ForeignKey('titles.Title', on_delete=models.CASCADE)

    class Meta:
        unique_together = (('list', 'title'),)


class UserList(BaseModel, DateCreatedModifiedMixin):
    name = models.CharField(_('название'), max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lists'
    )
    titles = models.ManyToManyField('titles.Title', through='UserListTitle')
    is_public = models.BooleanField(_('публичный?'), default=False)


class ViewedEpisode(BaseModel, DateCreatedMixin):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True
    )
    episode = models.ForeignKey(
        'translations.Episode',
        on_delete=models.CASCADE,
        null=False,
        related_name='viewed',
    )
    start_from = models.PositiveSmallIntegerField(
        _('Продолжить просмотр с (секунд)'), default=0
    )


class TitleRating(BaseModel, DateCreatedMixin):
    class RATES(models.IntegerChoices):
        one = 1
        two = 2
        three = 3
        four = 4
        five = 5
        six = 6
        seven = 7
        eight = 8
        nine = 9
        ten = 10

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.ForeignKey(
        'titles.Title', on_delete=models.CASCADE, related_name='ratings'
    )
    rate = models.PositiveSmallIntegerField(choices=RATES.choices)

    class Meta:
        unique_together = (('user', 'title'),)
