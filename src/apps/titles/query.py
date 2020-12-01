from django.db import models

from apps.core.query import BaseManager, SlugManager


def filter_queryset_by_enabled_title(
    queryset: models.QuerySet, prefix: str = '', condition: bool = False
):
    from .models import Title

    if prefix:
        prefix += '__'

    if condition and prefix:
        return queryset.exclude(
            models.Q(**{f'{prefix}isnull': False})
            & (
                models.Q(**{f'{prefix}slug': ''})
                | models.Q(**{f'{prefix}slug__isnull': True})
            )
        ).filter(
            models.Q(**{f'{prefix}isnull': True})
            | models.Q(**{f'{prefix}inner_status': Title.INNER_STATUSES.on},)
        )
    else:
        return queryset.exclude(
            models.Q(**{f'{prefix}slug': ''})
            | models.Q(**{f'{prefix}slug__isnull': True})
        ).filter(**{f'{prefix}inner_status': Title.INNER_STATUSES.on},)
