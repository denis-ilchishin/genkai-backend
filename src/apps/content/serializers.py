from rest_framework import serializers

from .models import Country, Genre, Studio


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = [
            'name',
            'slug',
        ]
        lookup_field = 'slug'
        extra_kwargs = {'url': {'lookup_field': 'slug'}}


class StudioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Studio
        fields = [
            'name',
            'slug',
        ]
        lookup_field = 'slug'
        extra_kwargs = {'url': {'lookup_field': 'slug'}}


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = [
            'name',
            'slug',
        ]
        lookup_field = 'slug'
        extra_kwargs = {'url': {'lookup_field': 'slug'}}
