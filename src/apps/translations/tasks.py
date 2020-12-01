from __future__ import absolute_import, unicode_literals

import logging

from celery import shared_task
from celery.app.control import Inspect

from config.celery import app

from .services import MoviesKodikUpdateService, SeriesKodikUpdateService

logger = logging.getLogger(__name__)


update_titles_queue_key = 'update_titles_queue_key'
broker_connection = app.broker_connection().default_channel.client


@shared_task
def update_titles(force: bool = False):
    """Update titles task.

    Args:
        force (bool, optional): Whether task should be executed even if it's already in queue or running. Defaults to False.
    """

    if force or broker_connection.incr(update_titles_queue_key) == 1:
        # queue up the task only the first time, or if has been forced
        DO_NOT_USE_update_title.delay()


@shared_task
def DO_NOT_USE_update_title():
    """Private task. Shouldn't be used, use instead "update_titles" task"""

    # Reset counter
    broker_connection.delete(update_titles_queue_key)

    try:
        SeriesKodikUpdateService().update()
        MoviesKodikUpdateService().update()
    except Exception:
        logger.exception()
