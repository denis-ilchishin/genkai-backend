from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Exists, F, IntegerField, OuterRef, Q, Subquery
from django.db.models.expressions import RawSQL
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework import generics, mixins, permissions, status
from rest_framework.response import Response
from rest_framework.settings import api_settings

from apps.core.generics import CreateAPIView
from apps.core.permissions import IsOwner
from apps.titles.models import Title

from . import models, query, serializers
from .permissions import IsNotCommentOwnerRate


class SQCount(Subquery):
    template = "(SELECT count(*) FROM (%(subquery)s) _count)"
    output_field = IntegerField()


class TitleCommentsList(generics.ListAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = serializers.TitleCommentSerializer
    ordering_fields = ('date_created', 'rating', 'has_rates')
    ordering = ('-date_created',)

    def get_queryset(self, **kwargs):
        return (
            query.annotate_rates(
                models.TitleComment.objects.enabled()
                .filter(reply_to__isnull=True)
                .select_related('user')
            )
            .annotate(
                rating=F('likes') - F('dislikes'),
                has_rates=Exists(
                    models.CommentRate.objects.filter(comment=OuterRef('pk'))
                ),
                replies=SQCount(
                    models.Comment.objects.filter(
                        tree_id=OuterRef('tree_id'), level__gt=0
                    ).only('pk')
                ),
            )
            .filter(title=self.title)
        )

    def list(self, request, *args, **kwargs):
        self.title = get_object_or_404(Title, slug=kwargs.get('title_slug'))
        return super().list(request, *args, **kwargs)


class RepliesList(generics.ListAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = serializers.CommenReplySerializer
    pagination_class = None

    def get_queryset(self):
        return query.annotate_rates(
            models.TitleComment.objects.enabled()
            .filter(level__gt=0, tree_id=self.comment.tree_id)
            .select_related('user', 'reply_to', 'reply_to__user')
        )

    def list(self, request, *args, **kwargs):
        self.comment = get_object_or_404(models.Comment, pk=kwargs.get('pk'))
        return super().list(request, *args, **kwargs)


class TitleCommentCreate(CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.TitleCommentCreateSerializer

    def get_response_serializer_class(self, instance):
        return (
            serializers.CommenReplySerializer
            if instance.reply_to
            else serializers.TitleCommentSerializer
        )


class CommentRateCreate(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated, IsOwner, IsNotCommentOwnerRate)
    queryset = models.CommentRate.objects
    serializer_class = serializers.CommentRateCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            comment_rate = self.queryset.get_or_none(
                user=request.user, comment=serializer.validated_data['comment']
            )
            if comment_rate:
                if comment_rate.rate == serializer.validated_data['rate']:
                    response_data = {
                        api_settings.NON_FIELD_ERRORS_KEY: _(
                            'Вы уже поставили %s этому комментарию'
                        )
                        % comment_rate.get_rate_display()
                    }
                    return Response(response_data, status=status.HTTP_400_BAD_REQUEST,)
                else:
                    comment_rate.delete()
        return super().create(request, *args, **kwargs)


class CommentRateDelete(generics.DestroyAPIView):
    permission_classes = (permissions.IsAuthenticated, IsOwner, IsNotCommentOwnerRate)
    queryset = models.CommentRate.objects.enabled()
    serializer_class = serializers.CommentRateRetrieveSerializer
