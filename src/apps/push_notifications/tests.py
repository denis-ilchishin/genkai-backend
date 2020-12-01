import json

from core.tests import JSON_CONTENT_TYPE, BaseTestCase

# class PushNotificationsEndpointsTest(BaseTestCase):
#     def setUp(self):
#         self.user, self.token = self._setup_test_user()

#     def test_push_notifications_subscribe_success(self):
#         data = {
#             'subscription': {
#                 'endpoint': 'https://fcm.googleapis.com/fcm/send/some_key_here',
#                 'expirationTime': None,
#                 'keys': {'p256dh': 'some_key_here', 'auth': 'some_key_here',},
#             },
#             'device': 'Some user agent',
#         }

#         response = self.client.post(
#             '/push-notifications/subscribe/',
#             json.dumps(data),
#             content_type=JSON_CONTENT_TYPE,
#             **self._get_auth_headers(self.token),
#         )

#         self.assertEqual(
#             response.status_code, 200,
#         )
