from importlib import import_module

from django.apps import AppConfig
from django.conf import settings


class BaseAppConfig(AppConfig):
    def ready(self):
        try:
            # Auto import signals module for every app
            __import__(f'{self.name}.signals')
        except ModuleNotFoundError:
            pass

        if settings.DEBUG:
            # import celery tasks for autoreloading
            try:
                # Auto import tasks module for every app
                __import__(f'{self.name}.tasks')
            except ModuleNotFoundError:
                pass
