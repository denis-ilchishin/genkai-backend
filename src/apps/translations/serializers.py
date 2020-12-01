from rest_framework import serializers

from apps.titles.serializers import BaseTitleSerializer, BaseTitleSerializerMeta

from .models import Episode, Translation, Translator


class UpdateTranslationTitleSerializer(BaseTitleSerializer):
    class Meta(BaseTitleSerializerMeta):
        fields = BaseTitleSerializerMeta.fields + ('type',)


class TranslatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Translator
        fields = ('id', 'slug', 'name')


class UpdateTranslationSerializer(serializers.ModelSerializer):
    title = UpdateTranslationTitleSerializer()
    translator = TranslatorSerializer()

    class Meta:
        model = Translation
        fields = ('id', 'title', 'translator', 'service')


class UpdateSerializer(serializers.ModelSerializer):
    translation = UpdateTranslationSerializer()

    class Meta:
        model = Episode
        fields = (
            'id',
            'number',
            'name',
            'translation',
            'date_created',
        )
