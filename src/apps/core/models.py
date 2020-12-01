from django.db import models
from django.utils import timezone
from mptt.models import MPTTModel

from .query import BaseManager, BaseTreeManager


class BaseModel(models.Model):

    objects = BaseManager()

    class Meta:
        abstract = True


class BaseTreeModel(MPTTModel):
    objects = BaseTreeManager()

    class Meta:
        abstract = True
