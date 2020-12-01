from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.widgets import AutocompleteSelect
from django.contrib.postgres.forms import SimpleArrayField
from django.forms.fields import CharField
from django.forms.widgets import Textarea

from .models import Title, WatchOrderItem


class TitleAdminForm(forms.ModelForm):
    other_names = SimpleArrayField(
        CharField(),
        delimiter=settings.ARRAY_FIELD_DELIMITER,
        widget=Textarea(),
        required=False,
    )
    tags = SimpleArrayField(
        CharField(),
        delimiter=settings.ARRAY_FIELD_DELIMITER,
        widget=Textarea(),
        required=False,
    )
    characters = SimpleArrayField(
        CharField(),
        delimiter=settings.ARRAY_FIELD_DELIMITER,
        widget=Textarea(),
        required=False,
    )

    class Meta:
        model = Title
        fields = '__all__'


class WatchOrderItemAdminForm(forms.ModelForm):
    class Meta:
        model = WatchOrderItem
        fields = '__all__'
        widgets = {
            'description': forms.TextInput(attrs={'size': 20}),
            'name': forms.TextInput(attrs={'size': 25}),
            'total_episodes': forms.TextInput(attrs={'size': 10}),
            'title': AutocompleteSelect(
                WatchOrderItem._meta.get_field('title').remote_field,
                admin.site,
                attrs={'data-width': 500},
            ),
        }
