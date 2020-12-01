from . import models


def get_user_rate(comment: models.Comment, user):
    return models.CommentRate.objects.get_or_none(comment=comment, user=user)
