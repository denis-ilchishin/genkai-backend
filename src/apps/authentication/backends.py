import hashlib
import hmac
import re
from collections import OrderedDict

from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.utils.translation import gettext_lazy as _

from apps.core.exceptions import SingleValidationError
from apps.users.models import User


class EmailBackend(ModelBackend):
    def authenticate(self, request, **kwargs):
        email = kwargs.get('email')
        password = kwargs.get('password')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            User().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user


class BaseSocialMediaBackend(ModelBackend):
    pass


class TelegramBackend(BaseSocialMediaBackend):
    def authenticate(self, request, data, create_user=False):
        data = data

        if not self.check_data_integrity(data):
            raise SingleValidationError(
                'Не удалось верефицировать запрос. Перезагрузите страницу и попробуйте еще раз',
            )

        try:
            user = User.objects.get(telegram_id=data['id'])
        except User.DoesNotExist:
            if create_user:
                user = User.objects.create_user_via_social_media(
                    username=data['username'], telegram_id=data['id']
                )
            else:
                user = None
        finally:
            if user is not None and self.user_can_authenticate(user):
                return user

    @classmethod
    def check_data_integrity(self, data: dict) -> bool:
        try:
            telegram_hash = data['hash']
            data.pop('hash', None)
        except KeyError:
            return False
        else:
            data_string = '\n'.join(
                [
                    f'{key}={value}'
                    for key, value in OrderedDict(sorted(data.items())).items()
                ]
            )
            secret_key = hashlib.sha256(settings.TELEGRAM_API_TOKEN.encode())
            verify_hash = hmac.new(
                key=secret_key.digest(),
                msg=data_string.encode(),
                digestmod=hashlib.sha256,
            ).hexdigest()

            return verify_hash == telegram_hash


telegram_backend = TelegramBackend()
