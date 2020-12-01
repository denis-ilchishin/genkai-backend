from pprint import pprint

from django.conf import settings
from django.core.cache import cache

from apps.content.models import Country, Genre, Studio
from apps.notifications.models import Notification
from apps.titles.models import Title
from apps.users.models import User, UserProfile


def _get_content_apps() -> dict:
    return {
        'genres': list(Genre.objects.enabled().values('slug', 'name')),
        'studios': list(Studio.objects.enabled().values('slug', 'name')),
        'countries': list(Country.objects.enabled().values('slug', 'name')),
    }


def _get_catalog_filter_max_year() -> int:
    queryset = Title.objects.enabled().filter(year__isnull=False)
    return queryset.order_by('-year').first().year if queryset.count() else 2100


def _get_catalog_filter_min_year() -> int:
    return (
        Title.objects.enabled().order_by('year').first().year
        if Title.objects.enabled().count()
        else 1950
    )


def get_frontend_app_config() -> dict:
    config = {
        'year_seasons': dict(Title.YEAR_SEASONS.choices),
        'statuses': dict(Title.STATUSES.choices),
        'sources': dict(Title.SOURCES.choices),
        'types': dict(Title.TYPES.choices),
        'age_ratings': dict(Title.AGE_RATINGS.choices),
        'release_days': dict(Title.RELEASE_DAYS.choices),
        'notification_types': dict(Notification.TYPES.choices),
        'sex': dict(UserProfile.SEX.choices),
        'movie_type': Title.TYPES.movie.value,
        'ongoing_status': Title.STATUSES.ongoing.value,
        'announce_status': Title.STATUSES.announce.value,
        'inputs': {
            'login': {
                'email': {'max_length': User._meta.get_field('email').max_length},
            },
            'titles': {
                'search': {
                    'min_length': settings.TITLES_SEARCH_MIN_LENGTH,
                    'max_length': settings.TITLES_SEARCH_MAX_LENGTH,
                }
            },
            'comments': {
                'comment': {'max_length': settings.COMMENTS_COMMENT_MAX_LENGTH,}
            },
            'register': {
                'email': {'max_length': User._meta.get_field('email').max_length,},
                'username': {
                    'min_length': settings.USERS_USERNAME_MIN_LENGTH,
                    'max_length': settings.USERS_USERNAME_MAX_LENGTH,
                },
                'password': {'min_length': settings.USERS_PASSWORD_MIN_LENGTH,},
            },
            'account': {
                'notifications': {
                    'max_selected': settings.NOTIFICATIONS_MAX_NUMBER_SELECTED
                },
                'profile': {
                    'about_myself': {
                        'max_length': settings.USERS_PROFILE_ABOUTMYSELF_MAX_LENGTH
                    }
                },
            },
        },
        'genres': [],
        'studios': [],
        'countries': [],
        # 'catalog_routes': _get_catalog_routes(),
    }

    config.update(_get_content_apps())

    config['inputs']['catalog'] = {
        'filter': {
            'max_year': _get_catalog_filter_max_year(),
            'min_year': _get_catalog_filter_min_year(),
        }
    }

    return config


# def _get_catalog_routes() -> dict:
#     key = 'config.routes'
#     if not (cached_catalog_routes := cache.get(key)):
#         cached_catalog_routes = {}

#         genres = Genre.objects.enabled().values('slug', 'name')

#         for value, text in Title.STATUSES.choices:
#             cached_catalog_routes[value] = {
#                 'field': 'status',
#                 'value': value,
#                 'text': text,
#             }

#         for value, text in Title.TYPES.choices:
#             cached_catalog_routes[value] = {
#                 'field': 'type',
#                 'value': value,
#                 'text': text,
#             }

#         for genre in genres:
#             cached_catalog_routes[genre['slug']] = {
#                 'field': 'genres',
#                 'value': [genre['slug']],
#                 'text': genre['name'],
#             }

#         cache.set(key, cached_catalog_routes, 60 * 60)
#     return cached_catalog_routes
