import time

from django.db.models import QuerySet
from django.shortcuts import render
from rest_framework import generics, permissions

from apps.titles.query import filter_queryset_by_enabled_title

from .models import Episode
from .serializers import UpdateSerializer


class Updates(generics.ListAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = UpdateSerializer
    queryset = (
        filter_queryset_by_enabled_title(Episode.objects.all(), 'translation__title',)
        .select_related('translation__translator', 'translation__title')
        .order_by('-date_created')
    )
