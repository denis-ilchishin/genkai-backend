import time

from core.tests import BaseTestCase

from apps.translations.models import Episode, Update
from apps.translations.services import (
    MoviesKodikUpdateService,
    SeriesKodikUpdateService,
)
from apps.users.models import UserSubscription


class UpdateTitlesTestCase(BaseTestCase):
    def setUp(self):
        pass

    def test_update(self):
        SeriesKodikUpdateService(is_testing=True).update()
        SeriesKodikUpdateService(is_testing=True).update()
        MoviesKodikUpdateService(is_testing=True).update()
        MoviesKodikUpdateService(is_testing=True).update()


class TranslationEndpointsTest(BaseTestCase):
    def test_translations_endpoints(self):
        self.assertEqual(self.client.get('/translations/updates/').status_code, 200)


# class UpdatesNotificationTest(BaseTestCase):
#     def setUp(self):
#         self.user, self.token = self._setup_test_user()
#         self._setup_test_titles()

#     def test_update_notifications(self):
#         update = Update.objects.create()
#         episode = Episode.objects.first()
#         UserSubscription.objects.create(
#             user=self.user,
#             title=episode.translation.title,
#             translator=episode.translation.translator,
#         )
#         update.added_episodes.add(episode)
#         self.assertEqual(self.user.notifications.count(), 1)
