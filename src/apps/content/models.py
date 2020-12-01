from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core import mixins, query
from apps.core.models import BaseModel


class Country(BaseModel, mixins.SlugMixin, mixins.DateCreatedModifiedMixin):
    objects = query.SlugManager()

    name = models.CharField(_('name'), max_length=255)

    class Meta:
        verbose_name = _('country')
        verbose_name_plural = _('countries')
        ordering = ('name',)

    def __str__(self):
        return self.name


class Genre(BaseModel, mixins.SlugMixin, mixins.DateCreatedModifiedMixin):
    objects = query.SlugManager()

    name = models.CharField(_('name'), max_length=255)

    class Meta:
        verbose_name = _('genre')
        verbose_name_plural = _('genres')
        ordering = ('name',)

    def __str__(self):
        return self.name


class Studio(BaseModel, mixins.SlugMixin, mixins.DateCreatedModifiedMixin):
    objects = query.SlugManager()

    name = models.CharField(_('name'), max_length=255)

    class Meta:
        verbose_name = _('studio')
        verbose_name_plural = _('studios')
        ordering = ('name',)

    def __str__(self):
        return self.name
