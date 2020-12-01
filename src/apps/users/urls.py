from django.urls import include, path

from apps.users.views import LastViewedTitles

from . import views

app_name = 'users'

urlpatterns = [
    path(
        'is_email_available/',
        views.IsEmailAvailable.as_view(),
        name='is_email_available',
    ),
    path(
        'is_username_available/',
        views.IsUsernameAvailable.as_view(),
        name='is_username_available',
    ),
    path('change-image/', views.ChangeImage.as_view(), name='change_image'),
    path('remove-image/', views.RemoveImage.as_view(), name='remove_image'),
    path(
        'title-ratings/',
        include(
            [
                path('', views.TitleRatingCreate.as_view(), name='title_rating_create'),
                path(
                    '<slug:title_slug>/',
                    views.TitleRatingRetrieve.as_view(),
                    name='title_rating_retrieve',
                ),
                path(
                    '<slug:title_slug>/delete',
                    views.TitleRatingRemove.as_view(),
                    name='title_rating_remove',
                ),
            ]
        ),
    ),
    path(
        'lists/',
        include(
            [
                path(
                    'titles/',
                    views.UserListTitlesCreate.as_view(),
                    name='lists-titles-create',
                ),
                path(
                    'titles/<int:pk>/',
                    views.UserListTitlesDelete.as_view(),
                    name='lists-titles-delete',
                ),
            ]
        ),
    ),
    path('last-viewed-titles/', views.LastViewedTitles.as_view()),
    path(
        'last-viewed-episode/<slug:title_slug>/',
        views.LastViewedEpisode.as_view(),
        name='last_viewed_episode',
    ),
    path('view-episode/', views.ViewEpisode.as_view(), name='view_episode',),
    path(
        'subscriptions/',
        include(
            [
                path(
                    '',
                    views.UserSubscriptionCreate.as_view(),
                    name='subscriptions-create',
                ),
                path(
                    '<int:pk>/',
                    views.UserSubscriptionDelete.as_view(),
                    name='subscriptions-delete',
                ),
            ]
        ),
    ),
]
