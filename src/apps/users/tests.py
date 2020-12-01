# from io import BytesIO

# from django.conf import settings
# from django.test import TestCase
# from django.urls import reverse

# from apps.content import models as content_models

# from . import models as user_models

# api_vitrual_host = settings.VIRTUAL_HOSTS['api']


# def create_user(**kwargs):
#     return user_models.User.objects.create(**kwargs)


# class UserAvaliability(TestCase):
#     username = 'test_user'
#     other_username = 'test_user2'
#     invalid_username = 'test_user2!@%#&*!)#()'
#     email = 'test@user.xyz'
#     other_email = 'othertest@user.xyz'
#     invalid_email = 'othert!./!#()est@user'

#     def setUp(self):
#         self.user = create_user(username=self.username, email=self.email)

#     def test_username_is_avaliable(self):
#         response = self.client.post(
#             reverse('users:is_username_available', urlconf=api_vitrual_host['urlconf']),
#             HTTP_HOST=api_vitrual_host['host'],
#             data={'username': self.other_username},
#         )
#         self.assertEqual(response.data['result'], True)

#     def test_username_is_not_avaliable(self):
#         response = self.client.post(
#             reverse('users:is_username_available', urlconf=api_vitrual_host['urlconf']),
#             HTTP_HOST=api_vitrual_host['host'],
#             data={'username': self.username},
#         )
#         self.assertEqual(response.data['result'], False)

#     def test_username_is_invalid(self):
#         response = self.client.post(
#             reverse('users:is_username_available', urlconf=api_vitrual_host['urlconf']),
#             HTTP_HOST=api_vitrual_host['host'],
#             data={'username': self.invalid_username},
#         )
#         self.assertEqual(response.data['result'], False)

#     def test_email_is_avaliable(self):
#         response = self.client.post(
#             reverse('users:is_email_available', urlconf=api_vitrual_host['urlconf']),
#             HTTP_HOST=api_vitrual_host['host'],
#             data={'email': self.other_email},
#         )
#         self.assertEqual(response.data['result'], True)

#     def test_email_is_not_avaliable(self):
#         response = self.client.post(
#             reverse('users:is_email_available', urlconf=api_vitrual_host['urlconf']),
#             HTTP_HOST=api_vitrual_host['host'],
#             data={'email': self.email},
#         )
#         self.assertEqual(response.data['result'], False)

#     def test_email_is_invalid(self):
#         response = self.client.post(
#             reverse('users:is_email_available', urlconf=api_vitrual_host['urlconf']),
#             HTTP_HOST=api_vitrual_host['host'],
#             data={'email': self.invalid_email},
#         )
#         self.assertEqual(response.data['result'], False)


# def create_title(**kwargs):
#     return content_models.Title.objects.create(**kwargs)


# USERNAME = 'username'
# PASSWORD = 'test'
# EMAIL = 'email@test.com'


# def authSetUp(test):
#     user = create_user(username=USERNAME, email=EMAIL)
#     user.set_password(PASSWORD)
#     user.save()

#     test.client.login(
#         username=getattr(user, user.__class__.USERNAME_FIELD), password=PASSWORD
#     )


# class UserImageCase(TestCase):
#     def setUp(self):
#         authSetUp(self)

#     def test_image_content_is_invalid(self):
#         image = BytesIO(b'mybinarydata')
#         image.name = 'image.jpg'
#         response = self.client.post(
#             reverse('users:change_image', urlconf=api_vitrual_host['urlconf']),
#             HTTP_HOST=api_vitrual_host['host'],
#             data={'image': image},
#         )
#         self.assertEqual(response.status_code, 400)
