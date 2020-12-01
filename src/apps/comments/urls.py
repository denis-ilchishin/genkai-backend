from django.urls import include, path

from . import views

app_name = 'comments'
urlpatterns = [
    path(
        'rates/',
        include(
            [
                path('', views.CommentRateCreate.as_view(), name='comment-rate-create'),
                path(
                    '<int:pk>/',
                    views.CommentRateDelete.as_view(),
                    name='comment-rate-delete',
                ),
            ]
        ),
    ),
    path(
        'replies/<int:pk>/', views.RepliesList.as_view(), name='comments-replies-list',
    ),
    path(
        'titles/',
        include(
            [
                path(
                    '',
                    views.TitleCommentCreate.as_view(),
                    name='title-comments-create',
                ),
                path(
                    '<slug:title_slug>/',
                    views.TitleCommentsList.as_view(),
                    name='title-comments-list',
                ),
            ]
        ),
    ),
]
