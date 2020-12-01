from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core import mixins, query
from apps.core.models import BaseModel
from apps.titles.query import filter_queryset_by_enabled_title

# from apps.titles.models import Title


class Resolver(models.Model):
    """ This is class for auto update of title. Using to map external objects of IDs to internal objects IDs """

    class MODELS(models.IntegerChoices):
        """Internal system models"""

        none = 0, _('none')
        translator = 1, _('translator')
        translation = 2, _('translation')
        title = 3, _('title')

    service = models.CharField(choices=settings.SERVICES.choices, max_length=30)
    model = models.SmallIntegerField(
        choices=MODELS.choices, null=False, default=MODELS.none
    )
    internal_id = models.PositiveIntegerField(db_index=True, null=True)
    external_id = models.CharField(max_length=255)

    objects = query.BaseManager()

    class Meta:
        verbose_name = _('resolver')
        verbose_name_plural = _('resolvers')

    def __str__(self):
        return '%s | %s - EXT [%s] == INT [%s]' % (
            self.get_service_display(),
            self.get_model_display(),
            self.external_id,
            self.internal_id,
        )


class Translator(BaseModel, mixins.SlugMixin, mixins.DateCreatedModifiedMixin):
    objects = query.SlugManager()

    name = models.CharField(_('name'), max_length=255)
    is_subtitles = models.BooleanField(_('субтитры?'), default=False)

    class Meta:
        verbose_name = _('translator')
        verbose_name_plural = _('translators')
        ordering = ('name',)

    def __str__(self):
        return self.name


class TranslationManager(query.BaseManager):
    def enabled(self):
        return filter_queryset_by_enabled_title((super().enabled(), 'title'))


class Translation(BaseModel, mixins.DateCreatedModifiedMixin):
    objects: TranslationManager = TranslationManager()

    title = models.ForeignKey(
        'titles.Title',
        on_delete=models.CASCADE,
        null=True,
        verbose_name=_('title'),
        related_name='translations',
        related_query_name='translation',
    )
    translator = models.ForeignKey(
        'Translator', on_delete=models.SET_NULL, null=True, verbose_name=_('translator')
    )
    url = models.URLField(_('url'), max_length=255, null=True, blank=True)
    external_id = models.CharField(max_length=255, null=True, db_index=True)
    service = models.CharField(
        choices=settings.SERVICES.choices, max_length=30, null=True
    )
    is_other = models.BooleanField(_('Прочее'), default=False)

    class Meta:
        verbose_name = _('translation')
        verbose_name_plural = _('translations')

    def __str__(self):
        return '%s [%s]' % (self.translator, self.title)


class EpisodeManager(query.BaseManager):
    def enabled(self):
        return filter_queryset_by_enabled_title(super().enabled(), 'translation__title')


class Episode(BaseModel, mixins.DateCreatedMixin):
    objects = EpisodeManager()

    translation = models.ForeignKey(
        'Translation',
        on_delete=models.CASCADE,
        related_name='episodes',
        related_query_name='episode',
    )
    number = models.PositiveSmallIntegerField()
    name = models.CharField(
        _('название эпизода'), max_length=255, default='', blank=True
    )
    url = models.URLField(_('url'), max_length=255)

    class Meta:
        get_latest_by = ['date_created']
        ordering = ['number']
        unique_together = [['translation', 'number']]

    def __str__(self):
        number = f' [Эпизод {self.number}]' if self.number else ''
        title = f' ({self.name})' if self.name else ''
        return '%s%s%s' % (self.translation, number, title)


class Update(BaseModel, mixins.DateCreatedMixin):
    added_episodes = models.ManyToManyField('Episode')
    without_errors = models.BooleanField(
        verbose_name=_('Updated without errors'), default=True
    )
