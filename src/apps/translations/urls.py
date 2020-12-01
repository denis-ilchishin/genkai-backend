from django.urls import include, path

from . import views

app_name = 'translations'

urlpatterns = [
    path('updates/', views.Updates.as_view(), name='updates_list'),
]
