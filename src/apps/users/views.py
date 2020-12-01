from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models.query import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import generics, permissions, status
from rest_framework.settings import api_settings
from rest_framework.views import APIView, Response

from apps.core.generics import CreateAPIView
from apps.core.permissions import IsOwner
from apps.titles.query import filter_queryset_by_enabled_title

from . import models, serializers


class IsEmailAvailable(APIView):
    def post(self, request, *args, **kwargs):
        try:
            email = request.data['email']

            for validator in models.User._meta.get_field('email').validators:
                validator(email)

            if not models.User.objects.filter(email=email).exists():
                return Response({'result': True})

        except ValidationError:
            pass

        return Response({'result': False})


class IsUsernameAvailable(APIView):
    def post(self, request, *args, **kwargs):
        try:
            username = request.data['username']

            for validator in models.User._meta.get_field('username').validators:
                validator(username)

            if not models.User.objects.filter(username=username).exists():
                return Response({'result': True})

        except ValidationError:
            pass

        return Response({'result': False})


class ChangeImage(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        image = request.data.get('image', None)

        try:
            request.user.profile.image.save(image.name, image, save=True)
            return Response(request.user.profile.image.urls)
        except ValidationError as e:
            from traceback import print_exc

            print_exc(10)
            return Response({'detail': e.message}, status=400)


class RemoveImage(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        if not request.user.profile.image:
            return Response({'detail': _('Аватар не существует')}, status=400)

        request.user.profile.image.storage.delete_old(request.user.profile.image.name)
        request.user.profile.image = None
        request.user.save()

        return Response(None, status=201)


class UserSubscriptionCreate(CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = models.UserSubscription.objects.enabled()
    serializer_class = serializers.UserSubscriptionCreateSerializer
    response_serializer_class = serializers.UserSubscriptionRetrieveSerializer


class UserSubscriptionDelete(generics.DestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = models.UserSubscription.objects.enabled()
    serializer_class = serializers.UserSubscriptionRetrieveSerializer


class LastViewedEpisode(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.ViewedEpisodeSerializer

    def get(self, request, title_slug):
        viewed_episode: models.ViewedEpisode = (
            models.ViewedEpisode.objects.enabled()
            .select_related('episode__translation')
            .filter(user=request.user, episode__translation__title__slug=title_slug)
            .order_by('-date_created')[:1]
            .first()
        )
        return Response(
            self.get_serializer(viewed_episode).data if viewed_episode else None,
            status=status.HTTP_200_OK,
        )


class LastViewedTitles(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.LastViewedTitleSerializer

    def get(self, request):
        viewed_episodes = (
            models.ViewedEpisode.objects.select_related(
                'episode',
                'episode__translation',
                'episode__translation__title',
                'episode__translation__translator',
            )
            .filter(
                id__in=(
                    filter_queryset_by_enabled_title(
                        models.ViewedEpisode.objects, 'episode__translation__title'
                    )
                    .filter(user=request.user)
                    .distinct('episode__translation__title')
                    .order_by('episode__translation__title', '-date_created')[
                        : settings.TITLES_HOME_PAGE_LIMIT
                    ]
                )
            )
            .order_by('-date_created')[: settings.TITLES_HOME_PAGE_LIMIT]
        )
        return Response(self.get_serializer(viewed_episodes, many=True).data)


class ViewEpisode(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = serializers.ViewedEpisodeSerializer

    def get_queryset(self) -> QuerySet:
        return models.ViewedEpisode.objects.enabled()

    def perform_create(self, serializer: serializers.ViewedEpisodeSerializer):
        new_viewed_episode: models.ViewedEpisode = models.ViewedEpisode(
            **serializer.validated_data
        )

        if new_viewed_episode.user and new_viewed_episode.start_from:
            viewed_episode = (
                self.get_queryset()
                .filter(user=new_viewed_episode.user)
                .order_by('-pk')[:1]
                .first()
            )
            if viewed_episode and viewed_episode.episode == new_viewed_episode.episode:
                viewed_episode.start_from = new_viewed_episode.start_from
                viewed_episode.save()
                return viewed_episode

        return serializer.save()


class TitleRatingCreate(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = models.TitleRating.objects
    serializer_class = serializers.TitleRatingSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if (
            title_rating := self.get_queryset().get_or_none(
                user=serializer.validated_data['user'],
                title=serializer.validated_data['title'],
            )
        ) :
            if title_rating.rate != serializer.validated_data['rate']:
                title_rating.rate = serializer.validated_data['rate']
                title_rating.save()
                return Response(
                    self.get_serializer_class()(title_rating).data,
                    status=status.HTTP_201_CREATED,
                )
            return Response(
                self.get_serializer_class()(title_rating).data,
                status=status.HTTP_200_OK,
            )

        return super().create(request, *args, **kwargs)


class TitleRatingRetrieve(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, title_slug):
        result = None
        if title_rating := models.TitleRating.objects.get_or_none(
            user=request.user, title__slug=title_slug
        ):
            result = serializers.TitleRatingSerializer(title_rating).data

        return Response(result, status=status.HTTP_200_OK)


class TitleRatingRemove(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def delete(self, request, title_slug):
        if title_rating := models.TitleRating.objects.get_or_none(
            user=request.user, title__slug=title_slug
        ):
            title_rating.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {api_settings.NON_FIELD_ERRORS_KEY: _('Оценка не существует')},
                status=status.HTTP_400_BAD_REQUEST,
            )


# class UserLists(generics.CreateAPIView):
#     permission_classes = (permissions.IsAuthenticated,)
#     queryset = models.UserList.objects.enabled()
#     serializer_class = serializers.UserListSerializer

#     def get_queryset(self):
#         """Restrict access, allow only self lists for request user"""
#         return super().get_queryset().filter(user=self.request.user)


class UserListTitlesCreate(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated, IsOwner('list.user'))
    queryset = models.UserListTitle.objects.enabled()
    serializer_class = serializers.UserListTitleSerializer


class UserListTitlesDelete(generics.DestroyAPIView):
    permission_classes = (permissions.IsAuthenticated, IsOwner('list.user'))
    queryset = models.UserListTitle.objects.enabled()
    serializer_class = serializers.UserListTitleSerializer
