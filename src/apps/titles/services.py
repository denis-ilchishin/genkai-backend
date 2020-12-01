from typing import Iterable

from django.contrib.postgres.search import TrigramSimilarity
from django.core.cache import cache
from django.db.models import Count, Q, QuerySet
from django.db.models.functions import Greatest

from apps.core.query import ArraySim

from .models import Title


def get_formated_relevant_data(title: Title) -> dict:
    return {
        'rating_total': str(title.relevant_data.rating_total),
        'rating_average': '{:0.2f}'.format(title.relevant_data.rating_average or 0),
        'views_total': str(title.relevant_data.views_total),
        'rank': str(title.relevant_data.rank),
        'rank_previous': str(title.relevant_data.rank_previous),
    }


def search(search_query: str, queryset: QuerySet = None) -> QuerySet:
    """
    Perform a search in Title's models.
    Returns ordered QuerySet
    """

    base_queryset = queryset if queryset else Title.objects.enabled()

    filtered_queryset = (
        base_queryset.annotate(
            similarity=Greatest(
                TrigramSimilarity('name', search_query),
                ArraySim('tags', search_query),
                ArraySim('other_names', search_query),
                ArraySim('characters', search_query),
            )
        )
        .filter(similarity__gte=0.3)
        .order_by('-similarity')
    )

    return filtered_queryset


def get_title_similars(title: Title, force=True) -> Iterable[Title]:
    queryset: QuerySet = Title.objects.enabled().exclude(pk=title.pk)

    cache_key = f'similars.{title.pk}'
    cache_timeout = 24 * 60 * 60  # one day
    similars = None
    if force or (similars := cache.get(cache_key)) is None:
        if title.watch_order_list:
            queryset = queryset.exclude(
                id__in=map(lambda x: x.pk, title.watch_order_list.titles)
            )

        similars = (
            queryset.annotate(
                similar_genres=Count('genres', filter=Q(genres__in=title.genres.all()))
            )
            .filter(similar_genres__gte=int(title.genres.count() * 0.9))
            .order_by('-similar_genres')[:10]
        )

        cache.set(cache_key, similars, cache_timeout)

    return similars

