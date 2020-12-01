from django.core.cache import cache
from django.urls import path
from django.views.decorators.cache import cache_page

from . import views

app_name = 'titles'

pages = {
    'titles/': {'view': views.Titles.as_view(), 'cache': False,},
    'titles/<slug:slug>/': {'view': views.Title.as_view(), 'cache': 5,},
    'populars/': {'view': views.Populars.as_view(), 'cache': 5,},
    'ongoings/': {'view': views.Ongoings.as_view(), 'cache': 5,},
    'current-season/': {'view': views.CurrentSeason.as_view(), 'cache': 5,},
    'latests/': {'view': views.Latests.as_view(), 'cache': 5,},
    'search/': {'view': views.Search.as_view(), 'cache': False,},
}

urlpatterns = [
    path(
        _path,
        cache_page(int(page['cache']) * 60)(page['view'])
        if page['cache']
        else page['view'],
    )
    for _path, page in pages.items()
]
