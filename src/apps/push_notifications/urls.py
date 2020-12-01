from django.urls import include, path

from . import views

app_name = 'push_notifications'

urlpatterns = [
    path('subscribe/', views.PushNotificationSubscription.as_view()),
]
