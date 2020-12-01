from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.titles.models import Title
from apps.users.serializers import UserBaseSerializer

from . import models, service


class BaseCommentSerializerMeta:
    model = models.Comment
    fields = (
        'id',
        'user',
        'text',
        'likes',
        'dislikes',
        'date_created',
        'date_modified',
        'group',
        'rate',  # request user's rate
    )


class BaseCommentSerializer(serializers.ModelSerializer):
    user = UserBaseSerializer()
    likes = serializers.SerializerMethodField()
    dislikes = serializers.SerializerMethodField()
    rate = serializers.SerializerMethodField()
    group = serializers.IntegerField(source='tree_id', read_only=True)

    class Meta(BaseCommentSerializerMeta):
        pass

    def get_rate(self, comment):
        if (
            'request' in self.context
            and (user := self.context['request'].user)
            and user.is_authenticated
        ):
            comment_rate = service.get_user_rate(comment, user)
            return (
                CommentRateRetrieveSerializer(comment_rate).data
                if comment_rate
                else None
            )
        else:
            return None

    def get_likes(self, comment):
        """
        Here we suppose that queryset already has aggregated number of likes 
        (e.g look apps.comments.views.TitleCommentList), to reduce number of db queries
        """
        return comment.likes if hasattr(comment, 'likes') else 0

    def get_dislikes(self, comment):
        """
        Here we suppose that queryset already has aggregated number of dislikes 
        (e.g look apps.comments.views.TitleCommentList), to reduce number of db queries
        """
        return comment.dislikes if hasattr(comment, 'dislikes') else 0


class CommentSerializer(BaseCommentSerializer):
    replies = serializers.SerializerMethodField()

    class Meta(BaseCommentSerializerMeta):
        fields = BaseCommentSerializerMeta.fields + ('replies',)

    def get_replies(self, comment):
        """
        Here we suppose that queryset already has replies attribute
        (e.g look apps.comments.views.TitleCommentList), to reduce number of db queries
        """
        return comment.replies if hasattr(comment, 'replies') else 0


class CommentReplyToUserSerializer(UserBaseSerializer):
    class Meta(UserBaseSerializer.Meta):
        fields = ('id', 'username')


class CommentReplyToSerializer(serializers.ModelSerializer):
    user = CommentReplyToUserSerializer()

    class Meta:
        model = models.Comment
        fields = (
            'id',
            'user',
        )


class CommenReplySerializer(BaseCommentSerializer):
    reply_to = CommentReplyToSerializer()

    class Meta(BaseCommentSerializerMeta):
        fields = BaseCommentSerializerMeta.fields + ('reply_to',)


class TitleCommentSerializer(CommentSerializer):
    title = serializers.SlugRelatedField(
        slug_field='slug', queryset=Title.objects.enabled(), allow_null=False
    )

    class Meta(CommentSerializer.Meta):
        model = models.TitleComment
        fields = CommentSerializer.Meta.fields + ('title',)


class TitleCommentCreateSerializer(TitleCommentSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta(TitleCommentSerializer.Meta):
        fields = ('user', 'title', 'reply_to', 'text')


class CommentRateCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    comment = serializers.PrimaryKeyRelatedField(
        queryset=models.Comment.objects.enabled()
    )

    class Meta:
        model = models.CommentRate
        fields = ('id', 'user', 'comment', 'rate')

    def get_unique_together_validators(self):
        """
        Overriding method to disable unique together checks on serializer.
        We do this to provide `toggle` effect. 
    !!! So we have to check whether the rate already exists to prevent throwing database unique together exception.
        """
        return []


class CommentRateRetrieveSerializer(serializers.ModelSerializer):
    user = UserBaseSerializer()
    comment = serializers.PrimaryKeyRelatedField(
        queryset=models.Comment.objects.enabled()
    )

    class Meta:
        model = models.CommentRate
        fields = ('id', 'user', 'comment', 'rate')
