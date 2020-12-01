from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.mixins import DateCreatedMixin, DateCreatedModifiedMixin
from apps.core.models import BaseModel, BaseTreeModel
from apps.core.query import BaseTreeManager


class CommentManager(BaseTreeManager):
    def enabled(self):
        return self.filter(inner_status=Comment.INNER_STATUSES.on)


class Comment(BaseTreeModel, DateCreatedModifiedMixin):
    class INNER_STATUSES(models.IntegerChoices):
        moder = 1, _('moderation')
        on = 2, _('on')

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='title_comments',
    )
    text = models.CharField(_('текст комментария'), max_length=1000)
    inner_status = models.PositiveSmallIntegerField(
        _('статус'), choices=INNER_STATUSES.choices, default=INNER_STATUSES.on,
    )
    reply_to = models.ForeignKey('self', on_delete=models.CASCADE, null=True)

    objects = CommentManager()

    class MPTTMeta:
        parent_attr = 'reply_to'


class CommentRate(BaseModel, DateCreatedMixin):
    class RATES(models.IntegerChoices):
        dislike = 0, _('дизлайк')
        like = 1, _('лайк')

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.ForeignKey(
        'Comment', on_delete=models.CASCADE, related_name='rates'
    )
    rate = models.PositiveSmallIntegerField(_('оценка'), choices=RATES.choices)

    class Meta:
        unique_together = [['user', 'comment']]


class TitleComment(Comment):
    title = models.ForeignKey(
        'titles.Title', on_delete=models.CASCADE, related_name='comments'
    )
