from django.utils.translation import gettext_lazy as _

from apps.core.permissions import RestBasePermissions


class IsNotCommentOwnerRate(RestBasePermissions):
    message = _('Вы не можете поставить лайк/дизлайк своему комменарию')

    def has_permission(self, request, view):
        if request.method in ['DELETE', 'PUT']:
            return True

        if request.user and request.user.is_authenticated:

            serializer = view.get_serializer(
                data={**request.data, 'user': request.user.id}
            )
            serializer.is_valid(raise_exception=True)
            comment = serializer.validated_data['comment']

            return comment.user != request.user

        return False

    def has_object_permission(self, request, view, obj):
        return bool(
            request.user
            and request.user.is_authenticated
            and obj.comment.user != request.user
        )
