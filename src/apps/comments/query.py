from django.db.models import Count, Q

from .models import CommentRate


def annotate_rates(queryset):
    return queryset.annotate(
        likes=Count('rates__rate', filter=Q(rates__rate=CommentRate.RATES.like)),
        dislikes=Count('rates__rate', filter=Q(rates__rate=CommentRate.RATES.dislike),),
    )
