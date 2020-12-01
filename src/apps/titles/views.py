import django_filters
from django.conf import settings
from django.db.models import OuterRef, Q, Subquery
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import cache_page
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.content.models import Country, Genre, Studio
from apps.translations.models import Episode

from . import models, serializers, services

last_episode_annotate = Subquery(
    (
        Episode.objects.filter(translation__title=OuterRef('pk'))
        .order_by('-number')
        .values('number')[:1]
    )
)


class TitleFilter(django_filters.FilterSet):
    genres = django_filters.ModelMultipleChoiceFilter(
        queryset=Genre.objects.enabled(),
        to_field_name='slug',
        field_name='genres__slug',
    )
    countries = django_filters.ModelMultipleChoiceFilter(
        queryset=Country.objects.enabled(),
        to_field_name='slug',
        field_name='countries__slug',
    )
    studios = django_filters.ModelMultipleChoiceFilter(
        queryset=Studio.objects.enabled(),
        to_field_name='slug',
        field_name='studios__slug',
    )
    year__gte = django_filters.NumberFilter(field_name='year', lookup_expr='gte')
    year__lte = django_filters.NumberFilter(field_name='year', lookup_expr='lte')

    class Meta:
        model = models.Title
        fields = [
            'year__gte',
            'year__lte',
            'year_season',
            'studios',
            'status',
            'source',
            'type',
            'age_rating',
        ]
        # filter_overrides = {
        #     BaseImageField: {'filter_class': django_filters.BooleanFilter,},
        # }


class Titles(generics.ListAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = serializers.TitleSerializer
    filterset_class = TitleFilter
    ordering_fields = [
        'relevant_data__rating_average',
        'relevant_data__rank',
        'relevant_data__views_total',
        'year',
        'name',
    ]
    ordering = ['-relevant_data__rating_average']

    def get_queryset(self):
        return (
            models.Title.objects.enabled()
            .select_related('relevant_data',)
            .prefetch_related(
                'translations',
                'translations__translator',
                'translations__episodes',
                'genres',
                'studios',
                'countries',
            )
            .annotate(last_episode=last_episode_annotate)
        )


class Title(generics.RetrieveAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = serializers.TitleSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        return (
            models.Title.objects.enabled()
            .select_related('relevant_data',)
            .prefetch_related(
                'translations',
                'translations__translator',
                'translations__episodes',
                'genres',
                'studios',
                'countries',
            )
            .annotate(last_episode=last_episode_annotate)
        )


class Populars(generics.ListAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = serializers.TitlePopularSerializer
    pagination_class = None

    @method_decorator(cache_page(settings.TITLES_HOME_PAGE_CACHE_TIMEOUT))
    def list(self, *args, **kwargs):
        return super().list(*args, **kwargs)

    def get_queryset(self):
        return (
            models.Title.objects.enabled()
            .select_related('relevant_data',)
            .filter(relevant_data__rank__gte=1)
            .order_by('relevant_data__rank')
        )[: settings.TITLES_HOME_PAGE_LIMIT]


class Ongoings(generics.ListAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = serializers.OngoingSerializer
    pagination_class = None

    def get_queryset(self):
        return (
            models.Title.objects.enabled()
            .filter(status=models.Title.STATUSES.ongoing)
            .select_related('relevant_data',)
            .prefetch_related('genres', 'studios', 'countries',)
            .annotate(last_episode=last_episode_annotate)
        )


class Wallpapers(generics.ListAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = serializers.TitleCurrentSeasonSerializer
    pagination_class = None

    def get_queryset(self):
        return (
            models.Title.objects.enabled()
            .filter(
                year=2020,  # TODO: remove hard-code
                year_season=models.Title.YEAR_SEASONS.spring,  # TODO: remove hard-code
                wallpaper__isnull=False,
                wallpaper_mobile__isnull=False,
            )
            .exclude(Q(wallpaper='') | Q(wallpaper_mobile=''))
        )


class CurrentSeason(generics.ListAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = serializers.CurrentSeasonSerializer
    pagination_class = None

    @method_decorator(cache_page(settings.TITLES_HOME_PAGE_CACHE_TIMEOUT))
    def list(self, *args, **kwargs):
        return super().list(*args, **kwargs)

    def get_queryset(self):
        return (
            models.Title.objects.enabled()
            .filter(
                year=2020,  # TODO: remove hard-code
                year_season=models.Title.YEAR_SEASONS.autumn,  # TODO: remove hard-code
            )
            .annotate(last_episode=last_episode_annotate)
        )[: settings.TITLES_HOME_PAGE_LIMIT]


class Latests(generics.ListAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = serializers.LatestsSerializer
    pagination_class = None

    @method_decorator(cache_page(settings.TITLES_HOME_PAGE_CACHE_TIMEOUT))
    def list(self, *args, **kwargs):
        print('cahce')
        return super().list(*args, **kwargs)

    def get_queryset(self):
        return models.Title.objects.enabled().order_by('-date_enabled')[
            : settings.TITLES_HOME_PAGE_LIMIT
        ]


class Search(APIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = serializers.SearchTitleSerializer

    def get(self, request):
        serializer = serializers.SearchQuerySerializer(data=request.query_params)
        if serializer.is_valid(raise_exception=True):
            queryset = services.search(
                serializer.validated_data['q'], models.Title.objects.enabled()
            )
            result = self.serializer_class(queryset, many=True).data

            return Response(result)
