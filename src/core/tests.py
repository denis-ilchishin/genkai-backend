import random
import string

from django.test import TestCase

JSON_CONTENT_TYPE = 'application/json'


class BaseTestCase(TestCase):
    def _setup_test_user(self):

        from django.contrib.auth import get_user_model
        from rest_framework.authtoken.models import Token

        user = get_user_model().objects.create(
            username=self._get_random_string(),
            email=f'{self._get_random_string()}@test.com',
            is_active=True,
        )
        token = Token.objects.get_or_create(user=user)[0].key

        return user, token

    def _get_auth_headers(self, token: str) -> dict:
        return {'HTTP_AUTHORIZATION': f'Token {token}'}

    def _get_random_string(self, length: int = 10):
        return ''.join(random.choice(string.ascii_lowercase) for i in range(length))

    def _setup_test_titles(self, number: int = 10):
        from apps.titles.models import Title
        from apps.translations.models import Translation, Translator, Episode

        for i in range(0, number):
            title = Title.objects.create(
                inner_status=Title.INNER_STATUSES.on,
                slug=self._get_random_string(),
                name=self._get_random_string(),
                status=Title.STATUSES.ongoing,
            )
            translator = Translator.objects.create(name=self._get_random_string())
            translation = Translation.objects.create(title=title, translator=translator)
            for j in range(1, number):
                Episode.objects.create(translation=translation, number=j)


DUMMY_CACHE_SETTINGS = {
    'CACHES': {'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}}
}
