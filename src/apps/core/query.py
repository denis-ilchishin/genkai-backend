from django.contrib.postgres.search import TrigramBase
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from mptt.models import TreeManager


class BaseManager(models.Manager):
    def enabled(self) -> models.QuerySet:
        return self.get_queryset()

    def get_or_none(self, *args, **kwargs):
        try:
            return self.get(*args, **kwargs)
        except ObjectDoesNotExist:
            return None


class BaseTreeManager(TreeManager):
    def enabled(self):
        return self

    def get_or_none(self, *args, **kwargs):
        try:
            return self.get(*args, **kwargs)
        except ObjectDoesNotExist:
            return None


class SlugManager(BaseManager):
    def enabled(self):
        return (
            super().enabled().exclude(models.Q(slug='') | models.Q(slug__isnull=True))
        )


class Rank(models.Func):
    function = 'DENSE_RANK'
    template = '%(function)s() OVER (ORDER BY %(expressions)s DESC)'


class ArraySim(TrigramBase):
    function = 'ARR_SIM'
    output_field = models.FloatField()
