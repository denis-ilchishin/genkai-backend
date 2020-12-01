import hashlib
from re import T

from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.functional import cached_property
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from apps.core import fields, mixins
from apps.core.models import BaseModel

from . import query, storages


def get_slug_hash(slug: str) -> str:
    hashing = hashlib.sha1()
    hashing.update(str(slug).encode())
    return hashing.hexdigest()


def title_poster_path(title, filename):
    if not title.slug:
        return 'temp/{}'.format(filename)
    else:
        return 'title/{}/posters/{}'.format(get_slug_hash(title.slug), filename)


def title_wallpaper_path(title, filename):
    if not title.slug:
        return 'temp/{}'.format(filename)
    else:
        return 'title/{}/wallpapers/{}'.format(get_slug_hash(title.slug), filename)


def title_wallpaper_mobile_path(title, filename):
    if not title.slug:
        return 'temp/{}'.format(filename)
    else:
        return 'title/{}/mobile_wallpapers/{}'.format(
            get_slug_hash(title.slug), filename
        )


# Create your models here.
class TitleManager(query.BaseManager):
    def enabled(self):
        return query.filter_queryset_by_enabled_title(super().enabled())


class TitleRelevantData(BaseModel):
    title = models.OneToOneField(
        'Title',
        primary_key=True,
        related_name='relevant_data',
        on_delete=models.CASCADE,
    )
    rating_total = models.PositiveIntegerField(default=0, editable=False)
    rating_average = models.DecimalField(
        max_digits=4, decimal_places=2, default=0, editable=False
    )
    views_total = models.PositiveIntegerField(default=0, editable=False)
    rank = models.PositiveIntegerField(default=0, editable=False)
    rank_previous = models.PositiveIntegerField(default=0, editable=False)


class Title(BaseModel, mixins.SlugMixin, mixins.DateCreatedModifiedMixin):
    objects = TitleManager()

    class INNER_STATUSES(models.TextChoices):
        off = 'off', _('off')
        moder = 'model', _('on moderation')
        slug = 'slug', _('slug duplicate')
        on = 'on', _('on')

    class STATUSES(models.TextChoices):
        released = 'released', _('завершенный')
        ongoing = 'ongoing', _('онгоинг')
        announce = 'announce', _('анонс')

    class YEAR_SEASONS(models.TextChoices):
        winter = 'winter', _('зима')
        spring = 'spring', _('весна')
        summer = 'summer', _('лето')
        autumn = 'autumn', _('осень')

    class SOURCES(models.TextChoices):
        manga = 'manga', _('манга')
        manhwa = 'manhwa', _('манхва')
        game = 'game', _('игра')
        novel = 'novel', _('ранобэ')
        original = 'original', _('оригинальная идея')
        book = 'book', _('книга')

    class TYPES(models.TextChoices):
        series = 'series', _('TV сериал')
        movie = 'movie', _('п/ф')
        ova = 'ova', _('OVA')
        ona = 'ona', _('ONA')
        special = 'special', _('спешл')

    class RELEASE_DAYS(models.TextChoices):
        monday = 'mon', _('понедельник')
        tuesday = 'tue', _('вторник')
        wednesday = 'wed', _('среда')
        thursday = 'thu', _('четверг')
        friday = 'fri', _('пятница')
        saturday = 'sat', _('суббота')
        sunday = 'sun', _('воскресенье')

    class AGE_RATINGS(models.TextChoices):
        g = 'G', _('G — нет возрастных ограничений')
        pg = 'PG', _('PG — рекомендуется присутствие родителей')
        pg_13 = 'PG-13', _('PG-13 — не желателен к просмотру до 13 лет')
        r = 'R', _('R — до 17 лет к просмотру только в присутствии родителей')
        nc_17 = 'NC-17', _('NC-17 — до 17 лет к просмотру запрещен')

    inner_status = models.CharField(
        _('inner_status'),
        choices=INNER_STATUSES.choices,
        default=INNER_STATUSES.moder,
        db_index=True,
        max_length=10,
    )
    season = models.SmallIntegerField(null=True, blank=True)
    poster = fields.BaseImageField(
        null=True, upload_to=title_poster_path, storage=storages.TitlePosterStorage(),
    )
    wallpaper = fields.BaseImageField(
        null=True,
        upload_to=title_wallpaper_path,
        storage=storages.TitleWallpaperStorage(),
        blank=True,
    )

    wallpaper_mobile = fields.BaseImageField(
        null=True,
        upload_to=title_wallpaper_mobile_path,
        storage=storages.TitleWallpaperMobileStorage(),
        blank=True,
    )
    shikimori_id = models.PositiveIntegerField(_('Shikimori ID'), null=True, blank=True)
    name = models.CharField(_('название'), max_length=255)
    duration = models.CharField(
        _('длительность эпизода'), max_length=10, blank=True, null=True
    )
    description = models.TextField()
    other_names = ArrayField(
        models.CharField(max_length=255),
        verbose_name=_('другие названия'),
        default=list,
        blank=True,
    )
    tags = ArrayField(
        models.CharField(max_length=255),
        verbose_name=_('тэги'),
        default=list,
        blank=True,
    )
    characters = ArrayField(
        models.CharField(max_length=255),
        verbose_name=_('персонажи'),
        default=list,
        blank=True,
    )
    total_episodes = models.CharField(
        _('общее кол-во эп.'), max_length=10, default='', blank=True
    )
    year = models.PositiveSmallIntegerField(
        _('год выхода'),
        validators=[MaxValueValidator(2100), MinValueValidator(1900)],
        null=True,
    )
    year_season = models.CharField(
        _('сезон года'),
        choices=YEAR_SEASONS.choices,
        null=True,
        blank=True,
        db_index=True,
        max_length=10,
    )
    status = models.CharField(
        _('статус'), choices=STATUSES.choices, null=True, db_index=True, max_length=10
    )
    age_rating = models.CharField(
        _('возрастной рейтинг'),
        choices=AGE_RATINGS.choices,
        null=True,
        blank=True,
        db_index=True,
        max_length=10,
    )
    source = models.CharField(
        _('первоисточник'),
        choices=SOURCES.choices,
        null=True,
        blank=True,
        max_length=10,
    )
    type = models.CharField(
        _('тип'), choices=TYPES.choices, null=True, db_index=True, max_length=10
    )
    release_day = models.CharField(
        _('день недели выхода серий'),
        choices=RELEASE_DAYS.choices,
        null=True,
        blank=True,
        max_length=3,
    )
    genres = models.ManyToManyField(
        'content.Genre', verbose_name=_('жанры'), blank=True
    )
    countries = models.ManyToManyField(
        'content.Country', verbose_name=_('страны'), blank=True
    )
    studios = models.ManyToManyField(
        'content.Studio', verbose_name=_('студии'), blank=True
    )

    date_enabled = models.DateTimeField(_('Дата активации'), null=True, editable=False)

    class Meta:
        verbose_name = _('тайтл')
        verbose_name_plural = _('тайтлы')
        indexes = [
            GinIndex(fields=['name']),
        ]

    def save(self, *args, **kwargs):
        if self.inner_status == self.INNER_STATUSES.on and self.date_enabled is None:
            self.date_enabled = now()

        return super().save(*args, **kwargs)

    def __str__(self):
        return '%s [SE:%s]' % (self.name, self.season)

    @cached_property
    def rating_total(self):
        return self.relevant_data.rating_total

    @cached_property
    def rating_average(self):
        return '{:0.2f}'.format(self.relevant_data.rating_average or 0)

    @cached_property
    def rating_best(self):
        if self.ratings.count():
            return self.ratings.all().order_by('-rate')[:1].first().rate
        else:
            return None

    @cached_property
    def watch_order_list(self):
        return WatchOrderList.objects.get_or_none(watchorderitem__title=self)


class WatchOrderList(BaseModel):
    class Meta:
        verbose_name = _('порядок просмотра')
        verbose_name_plural = _('порядки просмотра')

    @cached_property
    def titles(self):
        return tuple(
            watchorderitem.title
            for watchorderitem in self.watchorderitem_set.all()
            if watchorderitem.title
        )

    def __str__(self):
        return ', '.join(
            map(
                lambda x: x.title.name if x.title else x.name,
                self.watchorderitem_set.all(),
            )
        )


class WatchOrderManager(query.BaseManager):
    def enabled(self):
        return query.filter_queryset_by_enabled_title(super().enabled(), 'title', True)


class WatchOrderItem(BaseModel):
    watch_order_list = models.ForeignKey('WatchOrderList', on_delete=models.CASCADE)
    title = models.OneToOneField(
        'Title',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_('тайтл'),
    )
    description = models.CharField(_('описание'), max_length=255, null=True, blank=True)

    name = Title._meta.get_field('name')
    name.blank = True
    name.null = True

    type = Title._meta.get_field('type')
    type.blank = True
    type.null = True

    year = Title._meta.get_field('year')
    year.blank = True
    year.null = True

    total_episodes = Title._meta.get_field('total_episodes')
    total_episodes.blank = True
    total_episodes.null = True

    ordering = models.PositiveSmallIntegerField()

    objects = WatchOrderManager()

    class Meta:
        ordering = ('ordering',)
        verbose_name = _('строка порядка просмотра')

    def __str__(self):
        return str(self.pk)


@receiver(post_save, sender=Title, dispatch_uid='create_relevant_data')
def create_relevant_data(sender, instance, created, **kwargs):
    if created:
        TitleRelevantData.objects.create(title=instance)
