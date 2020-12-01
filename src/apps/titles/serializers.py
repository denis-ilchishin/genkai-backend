from typing import Union

from django.core import validators
from rest_framework import serializers

from apps.content.serializers import (
    CountrySerializer,
    GenreSerializer,
    StudioSerializer,
)
from apps.translations.models import Episode, Translation, Translator

from . import services
from .models import Title, WatchOrderItem, WatchOrderList


def get_title_serializer_class(serializer_fields: dict = {}):
    """Generate title serializer class

    Args:
        fields (dict): serializer fields
        
        Example of `fields` arg:
        {
            "fieldname": {
                "value": serializers.Field(),
                "method": somemethod # if "value" is class of serializers.SerializerMethodField
            }
        }

    Returns:
        serializers.ModelSerializer: generated Title serializer class
    """

    class _TitleSerializerMeta:
        model = Title
        fields = ('name', 'slug', 'poster') + tuple(serializer_fields.keys())
        lookup_field = 'slug'
        extra_kwargs = {'url': {'lookup_field': 'slug'}}

    class _TitleSerializer(serializers.ModelSerializer):
        poster = serializers.SerializerMethodField()

        class Meta(_TitleSerializerMeta):
            pass

        def __init__(self, *args, **kwargs):
            for field_name, field in serializer_fields:
                setattr(self, field_name, field['value'])
                if isinstance(field['value'], serializers.SerializerMethodField):
                    setattr(
                        self,
                        f'get_{field_name}'
                        if field['value'].method_name is None
                        else field['value'].method_name,
                        field['method'],
                    )
            super().__init__(*args, **kwargs)

        def get_poster(self, title):
            return title.poster.urls

        def get_relevant_data(self, title):
            return services.get_formated_relevant_data(title)

        def get_last_episode(self, title):
            return title.last_episode

    return _TitleSerializer


class BaseTitleSerializerMeta:
    model = Title
    fields = ('name', 'slug', 'poster')
    lookup_field = 'slug'
    extra_kwargs = {'url': {'lookup_field': 'slug'}}


class BaseTitleSerializer(serializers.ModelSerializer):
    poster = serializers.SerializerMethodField()

    class Meta(BaseTitleSerializerMeta):
        pass

    def get_poster(self, title):
        return title.poster.urls

    def get_relevant_data(self, title):
        return services.get_formated_relevant_data(title)

    def get_last_episode(self, title):
        return title.last_episode if hasattr(title, 'last_episode') else None


class CurrentSeasonSerializer(BaseTitleSerializer):
    genres = GenreSerializer(many=True)
    relevant_data = serializers.SerializerMethodField()
    last_episode = serializers.SerializerMethodField()

    class Meta(BaseTitleSerializerMeta):
        fields = BaseTitleSerializerMeta.fields + (
            'genres',
            'year',
            'type',
            'relevant_data',
            'last_episode',
            'total_episodes',
        )


class TitleCurrentSeasonSerializer(BaseTitleSerializer):
    class Meta(BaseTitleSerializerMeta):
        pass


class TranslatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Translator
        fields = (
            'id',
            'name',
            'slug',
            'date_created',
            'date_modified',
        )
        lookup_field = 'slug'
        extra_kwargs = {'url': {'lookup_field': 'slug'}}


class EpisodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Episode
        fields = ('id', 'number', 'url', 'name')


class TranslationSerializer(serializers.ModelSerializer):
    episodes = EpisodeSerializer(many=True)
    translator = TranslatorSerializer()
    service = serializers.CharField()

    class Meta:
        model = Translation
        fields = ('id', 'translator', 'service', 'url', 'episodes', 'is_other')


class TitlePopularSerializer(BaseTitleSerializer):
    relevant_data = serializers.SerializerMethodField()

    class Meta(BaseTitleSerializerMeta):
        fields = BaseTitleSerializerMeta.fields + (
            'poster',
            'relevant_data',
            'status',
            'type',
        )


class OngoingSerializer(BaseTitleSerializer):
    other_names = serializers.ListField(child=serializers.CharField())
    genres = GenreSerializer(many=True)
    relevant_data = serializers.SerializerMethodField()
    last_episode = serializers.SerializerMethodField()

    class Meta(BaseTitleSerializerMeta):
        fields = BaseTitleSerializerMeta.fields + (
            'other_names',
            'release_day',
            'genres',
            'studios',
            'duration',
            'description',
            'year',
            'type',
            'relevant_data',
            'last_episode',
            'total_episodes',
        )


class WatchOrderTitleSerializer(BaseTitleSerializer):
    class Meta(BaseTitleSerializerMeta):
        fields = ('name', 'slug', 'type', 'year', 'total_episodes')


class WatchOrderSerializer(serializers.ModelSerializer):
    title = WatchOrderTitleSerializer()

    class Meta:
        model = WatchOrderItem
        fields = (
            'title',
            'description',
            'name',
            'type',
            'year',
            'total_episodes',
            'ordering',
        )


class WatchOrderListSerializer(serializers.ModelSerializer):
    titles = WatchOrderSerializer(source='watchorderitem_set', many=True)

    class Meta:
        model = WatchOrderList
        fields = ('titles',)


class TitleSerializer(BaseTitleSerializer):
    other_names = serializers.ListField(child=serializers.CharField())
    characters = serializers.ListField(child=serializers.CharField())
    tags = serializers.ListField(child=serializers.CharField())
    countries = CountrySerializer(many=True)
    genres = GenreSerializer(many=True)
    studios = StudioSerializer(many=True)
    translations = TranslationSerializer(many=True)
    watch_orders = serializers.SerializerMethodField()
    relevant_data = serializers.SerializerMethodField()
    last_episode = serializers.SerializerMethodField()
    similars = serializers.SerializerMethodField()

    class Meta(BaseTitleSerializerMeta):
        fields = BaseTitleSerializerMeta.fields + (
            'other_names',
            'release_day',
            'countries',
            'genres',
            'studios',
            'duration',
            'description',
            'source',
            'translations',
            'season',
            'poster',
            'year',
            'year_season',
            'characters',
            'tags',
            'age_rating',
            'status',
            'type',
            'relevant_data',
            'last_episode',
            'total_episodes',
            'date_enabled',
            'watch_orders',
            'similars',
        )

    def get_similars(self, title):
        return get_title_serializer_class()(
            services.get_title_similars(title), many=True
        ).data

    def get_watch_orders(self, title):
        return (
            WatchOrderSerializer(
                title.watch_order_list.watchorderitem_set.enabled(), many=True
            ).data
            if title.watch_order_list
            and title.watch_order_list.watchorderitem_set.enabled().count() > 1
            else None
        )


class SearchTitleSerializer(BaseTitleSerializer):
    class Meta(BaseTitleSerializerMeta):
        fields = BaseTitleSerializerMeta.fields + ('year', 'type', 'status')


class SearchQuerySerializer(serializers.Serializer):
    q = serializers.CharField(
        validators=[validators.MinLengthValidator(3), validators.MaxLengthValidator(50)]
    )


class LatestsSerializer(BaseTitleSerializer):
    genres = GenreSerializer(many=True)

    class Meta(BaseTitleSerializerMeta):
        fields = BaseTitleSerializerMeta.fields + ('year', 'type', 'genres',)
