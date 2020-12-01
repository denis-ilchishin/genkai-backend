from __future__ import absolute_import, unicode_literals

import logging
from datetime import datetime, timedelta

from celery import shared_task
from django.conf import settings
from django.db.models import Avg, Count, Q
from django.utils.timezone import now

from apps.core.query import Rank
from apps.titles.models import Title, TitleRelevantData
from apps.users.models import ViewedEpisode

from .models import Title, TitleRelevantData

logger = logging.getLogger(__name__)


@shared_task
def update_title_ranks():
    logger.info('Updating title\'s rank')
    try:
        titles = (
            Title.objects.enabled()
            .annotate(
                count=Count(
                    'translation__episode__viewed',
                    filter=Q(
                        translation__episode__viewed__date_created__gte=now()
                        - timedelta(days=settings.TITLES_RANK_EPISODES_DAYS_COUNT)
                    ),
                ),
                new_rank=Rank('count'),
            )
            .distinct()
        )

        for title in titles:
            title.relevant_data.rank_previous = title.relevant_data.rank
            title.relevant_data.rank = title.new_rank
            title.relevant_data.save()

        logger.info('Successfully updated title\'s ranks')
    except Exception as ex:
        logger.exception(ex)


@shared_task
def update_title_viewes_and_ratings():
    logger.info('Updating title\'s views and ratings')

    try:
        for title in Title.objects.enabled():
            # if for some reason we title doesn't have relevant_data - create it
            if not title.relevant_data:
                TitleRelevantData.objects.create(title=title)

            # total number of user ratings for this title
            title.relevant_data.rating_total = title.ratings.count()

            # averate user rating's rate for this title
            title.relevant_data.rating_average = (
                title.ratings.aggregate(Avg('rate'))['rate__avg'] or 0
            )

            views_queryset = ViewedEpisode.objects.filter(
                episode__translation__title=title
            )

            # title total views
            title.relevant_data.views_total = views_queryset.count()

            title.relevant_data.save()
        logger.info('Successfully updated title\'s views and ratings')

    except Exception as ex:
        logger.exception(ex)
