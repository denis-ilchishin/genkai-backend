from django.urls import include, path

from apps.notifications.views import NotificationList

from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.NotificationList.as_view()),
    path(
        'seen/',
        include(
            [
                path('all/', views.NotificationSeenAll.as_view()),
                path('selected/', views.NotificationSeenSelected.as_view()),
                path('<int:pk>/', views.NotificationSeen.as_view()),
            ]
        ),
    ),
    path(
        'delete/',
        include(
            [
                path('all/', views.NotificationDeleteAll.as_view()),
                path('selected/', views.NotificationDeleteSelected.as_view()),
                path('<int:pk>/', views.NotificationDelete.as_view()),
            ]
        ),
    ),
]
