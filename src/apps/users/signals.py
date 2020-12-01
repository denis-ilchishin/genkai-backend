from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UserList, UserProfile


def _create_default_lists(user):
    for name in [
        'Смотрю',
        'Пересматриваю',
        'Просмотрено',
        'Отложено',
        'Брошено',
    ]:
        UserList.objects.create(name=name, user=user)


def _create_user_profile(user):
    UserProfile.objects.create(user=user)


@receiver(post_save, sender=settings.AUTH_USER_MODEL, dispatch_uid='create_user_signal')
def create_user_signal(**kwargs):
    if kwargs.get('created'):
        # newly created users
        _create_default_lists(kwargs.get('instance'))
        _create_user_profile(kwargs.get('instance'))
    else:
        pass
