from django.contrib import admin
from django.utils.translation import gettext_lazy as _


from .models import Country, Genre, Studio


@admin.register(Genre,)
class GenreAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Studio,)
class StudioAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Country,)
class CountryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
