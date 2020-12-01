from adminsortable2.admin import SortableInlineAdminMixin
from django.contrib import admin
from django.contrib.admin.views.autocomplete import AutocompleteJsonView
from django.db.models import Q
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from nested_admin import NestedTabularInline

from apps.core.fields import BaseImageField
from apps.core.widgets import AdminImageWidget

from . import forms
from .models import Title, WatchOrderItem, WatchOrderList


def turn_on(modeladmin, request, queryset):
    queryset.update(inner_status=Title.INNER_STATUSES.on)


def turn_off(modeladmin, request, queryset):
    queryset.update(inner_status=Title.INNER_STATUSES.off, slug='')


class TitleAutocompleteView(AutocompleteJsonView):
    def get_queryset(self):
        return super().get_queryset().exclude(inner_status=Title.INNER_STATUSES.off)


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    class PosterFilter(admin.SimpleListFilter):
        title = 'Poster'
        parameter_name = 'poster'

        def lookups(self, request, model_admin):
            return [
                ('has_poster', 'С постером'),
                ('no_poster', 'Без постера'),
            ]

        def queryset(self, request, queryset):
            if self.value() == 'has_poster':
                return (
                    queryset.distinct()
                    .filter(poster__isnull=False)
                    .exclude(poster__exact='')
                )
            elif self.value():
                return queryset.distinct().filter(
                    Q(poster__isnull=True) | Q(poster__exact='')
                )

    fieldsets = (
        (
            'Main',
            {
                'fields': (
                    'shikimori_id',
                    'name',
                    'inner_status',
                    'slug',
                    'year',
                    'season',
                    'status',
                    'type',
                    'description',
                    'translations_data',
                    'watch_order_data',
                )
            },
        ),
        (
            'Data',
            {
                'fields': (
                    'total_episodes',
                    'duration',
                    'tags',
                    'other_names',
                    'characters',
                    'year_season',
                    'age_rating',
                    'source',
                    'release_day',
                    'genres',
                    'countries',
                    'studios',
                ),
            },
        ),
        ('Images', {'fields': ('poster', 'wallpaper', 'wallpaper_mobile'),}),
        ('Relevant Data', {'fields': ('relevant_data_text',)}),
    )
    list_display = (
        'id',
        'name',
        'shikimori_id',
        'type',
        'season',
        'status',
        'year',
        'inner_status',
        'date_created',
    )
    list_display_links = ('id', 'name')
    list_editable = ('shikimori_id', 'status', 'inner_status')
    list_filter = (
        'type',
        'inner_status',
        'status',
        PosterFilter,
    )
    actions = (turn_on, turn_off)
    prepopulated_fields = {'slug': ('name',)}
    form = forms.TitleAdminForm
    search_fields = ('name', 'id', 'shikimori_id', 'other_names', 'slug')
    readonly_fields = ('translations_data', 'relevant_data_text', 'watch_order_data')
    filter_horizontal = ('genres', 'countries', 'studios')
    list_per_page = 50
    formfield_overrides = {BaseImageField: {'widget': AdminImageWidget}}

    def autocomplete_view(self, request):
        return TitleAutocompleteView.as_view(model_admin=self)(request)

    def translations_data(self, title):
        result = ''
        for translation in title.translations.all():
            if result:
                result += '<br>'

            url = reverse(
                'admin:translations_translation_change', args=(translation.id,)
            )
            result += f'<a href="{url}">{translation.translator.name} - {translation.episodes.count()} эп.</a>'
        return mark_safe(result)

    translations_data.short_description = _('Озвучки/Переводы')

    def relevant_data_text(self, title):
        result = '<table width="100%">'
        fields = [
            'rating_total',
            'rating_average',
            'views_total',
            'rank',
            'rank_previous',
        ]
        for field in fields:
            result += f'<tr><td>{title.relevant_data._meta.get_field(field).verbose_name}</td><td>{getattr(title.relevant_data, field)}</td><tr>'

        result += '</table>'
        return mark_safe(result)

    relevant_data_text.short_description = _('Актуальная инфа')

    def watch_order_data(self, title):
        if watch_order_list := WatchOrderList.objects.get_or_none(
            watchorderitem__title=title
        ):

            url = reverse(
                'admin:titles_watchorderlist_change', args=(watch_order_list.id,)
            )
            return mark_safe(f'<a href="{url}">Перейти</a>')
        else:
            url = reverse('admin:titles_watchorderlist_add')
            return mark_safe(f'<a href="{url}">Добавить</a>')

    watch_order_data.short_description = _('Порядок просмотра')


class WatchOrderInline(SortableInlineAdminMixin, admin.TabularInline):
    model = WatchOrderItem
    extra = 0
    min_num = 1
    exclude = ('_active',)
    fieldsets = (
        (None, {'fields': ('title', 'ordering', 'description',)},),
        (
            'Другое',
            {
                'classes': ('collapse',),
                'fields': ('name', 'type', 'year', 'total_episodes'),
            },
        ),
    )

    form = forms.WatchOrderItemAdminForm


@admin.register(WatchOrderList)
class WatchOrderAdminList(admin.ModelAdmin):
    exclude = ('_active', 'titles')
    inlines = (WatchOrderInline,)
    search_fields = (
        'titles__title__pk',
        'titles__title__name',
        'titles__title__slug',
    )
