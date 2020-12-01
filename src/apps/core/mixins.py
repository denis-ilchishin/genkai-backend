from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .fields import SlugField
from .validators import slug_validator


class DateCreatedMixin(models.Model):
    date_created = models.DateTimeField(_('date created'), default=timezone.now)

    class Meta:
        abstract = True


class DateCreatedModifiedMixin(models.Model):
    date_created = models.DateTimeField(_('date created'), default=timezone.now)
    date_modified = models.DateTimeField(_('date modified'), default=timezone.now)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.date_modified = timezone.now()
        super().save(*args, **kwargs)


class SlugMixin(models.Model):
    slug = SlugField(
        max_length=255, default='', blank=True, validators=[slug_validator]
    )

    class Meta:
        abstract = True
