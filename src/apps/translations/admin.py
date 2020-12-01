import re
from re import search

from cryptography.utils import read_only_property
from django.contrib import admin
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .models import Episode, Resolver, Translation, Translator, Update


@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    search_fields = ('id', 'translation__id')
    exclude = ('date_created',)


class EpisodesInline(admin.StackedInline):
    model = Episode
    fieldsets = (('', {'fields': ('number', 'name', 'url', 'player')},),)
    extra = 0
    readonly_fields = ('player',)

    def player(self, episode):
        return mark_safe(render_to_string('fields/player.html', {'url': episode.url}),)

    player.short_description = _('Плеер')


@admin.register(Translation)
class TranslationAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'translator')
    search_fields = ('title__name', 'id', 'title__id', 'external_id')
    readonly_fields = ('player',)
    fieldsets = (
        (
            '',
            {
                'fields': (
                    'title',
                    'translator',
                    'url',
                    'external_id',
                    'service',
                    'is_other',
                    'player',
                )
            },
        ),
    )
    autocomplete_fields = ('title',)

    def player(self, translation):
        return mark_safe(
            render_to_string('fields/player.html', {'url': translation.url}),
        )

    player.short_description = _('Плеер')

    inlines = (EpisodesInline,)

    class Media:
        js = ('js/admin/player.js',)


@admin.register(Translator)
class TranslatorAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('id', 'name', 'slug')
    list_filter = ('is_subtitles',)


@admin.register(Update)
class UpdateAdmin(admin.ModelAdmin):
    list_display = ('id', 'date_created', 'number_of_new_episodes', 'without_errors')
    fieldsets = (
        ('', {'fields': ('date_created', 'without_errors', 'number_of_new_episodes')},),
    )

    readonly_fields = ('date_created', 'without_errors', 'number_of_new_episodes')

    def number_of_new_episodes(self, update: Update):
        return update.added_episodes.count()

    number_of_new_episodes.short_description = _('Number of new episodes')


@admin.register(Resolver)
class ResolverAdmin(admin.ModelAdmin):
    search_fields = ('external_id',)
    pass
