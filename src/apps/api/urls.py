from django.urls import include, path
from django.views.decorators.cache import cache_page

from . import views

app_name = 'api'

urlpatterns = [
    path(
        'frontend/',
        include(
            [
                path('home/', cache_page(60 * 5)(views.FrontendHome.as_view())),
                path('config/', cache_page(60 * 5)(views.FrontendConfig.as_view())),
            ]
        ),
    ),
    path('sitemap/', views.Sitemap.as_view()),
]
