import json

from core.tests import BaseTestCase


class TitlesEndpointsTest(BaseTestCase):
    def setUp(self):
        self._setup_test_titles()

    def _get_endpoints(self) -> list:
        return [
            'titles',
            'populars',
            'current-season',
            'latests',
        ]

    def test_titles_endpoints(self):
        for endpoint in self._get_endpoints():
            response = self.client.get(f'/titles/{endpoint}/')
            self.assertEqual(response.status_code, 200)
            self.assertIsInstance(
                json.loads(response.content), (dict, list),
            )
