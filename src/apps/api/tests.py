from core.tests import DUMMY_CACHE_SETTINGS, BaseTestCase
from django.contrib.auth import get_user_model
from django.test import override_settings

from apps.titles.models import Title
from apps.translations.models import Episode, Translation, Translator
from rest_framework.authtoken.models import Token


class BaseApiEndpointsTests(BaseTestCase):
    def setUp(self):
        self.title = Title.objects.create(
            inner_status=Title.INNER_STATUSES.on,
            slug='test',
            name='test',
            status=Title.STATUSES.ongoing,
        )
        self.translator = Translator.objects.create(name='test')
        self.translation = Translation.objects.create(
            title=self.title, translator=self.translator
        )
        self.episode = Episode.objects.create(translation=self.translation, number=1)

    @override_settings(**DUMMY_CACHE_SETTINGS)
    def test_api_endpoints(self):
        self.assertEqual(self.client.get('/frontend/config/').status_code, 200)
        self.assertEqual(self.client.get('/frontend/home/').status_code, 200)
        self.assertEqual(self.client.get('/sitemap/').status_code, 200)


# class AuthenticationTest(BaseTestCase):
#     def setUp(self):
#         self.password = '123456'
#         self.email = 'user@test.com'
#         self.user = get_user_model().objects.create(
#             username='user', email=self.email, is_active=True
#         )
#         self.user.set_password(self.password)
#         self.user.save()
#         self.token = Token.objects.get_or_create(user=self.user)[0].key

#     def test_user_data_not_autheticated(self):
#         self.assertEqual(self.client.get('/auth/data/').status_code, 401)

#     def test_user_data_success(self):
#         self.assertEqual(
#             self.client.get(
#                 '/auth/data/', **self._get_auth_headers(self.token)
#             ).status_code,
#             200,
#         )

#     def test_user_login_success(self):
#         data = {
#             'username': self.email,
#             'password': self.password,
#         }

#         response = self.client.post('/auth/login/', data)
#         self.assertEqual(
#             response.status_code, 200,
#         )

#     def test_user_login_incorrect_email(self):
#         data = {
#             'username': self.email + 'incorrect',
#             'password': self.password,
#         }

#         response = self.client.post('/auth/login/', data)
#         self.assertEqual(
#             response.status_code, 400,
#         )

#     def test_user_login_incorrect_password(self):
#         data = {
#             'username': self.email,
#             'password': self.password + 'incorrect',
#         }

#         response = self.client.post('/auth/login/', data)
#         self.assertEqual(
#             response.status_code, 400,
#         )

#     def test_user_login_missing_email(self):
#         data = {
#             'password': self.password,
#         }

#         response = self.client.post('/auth/login/', data)
#         self.assertEqual(
#             response.status_code, 400,
#         )

#     def test_user_login_missing_password(self):
#         data = {
#             'username': self.email,
#         }

#         response = self.client.post('/auth/login/', data)
#         self.assertEqual(
#             response.status_code, 400,
#         )
