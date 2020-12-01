import operator

from django.utils.translation import gettext_lazy as _
from rest_framework.permissions import BasePermission as RestBasePermissions

DEFAULT_MESSAGE = _('Доступ запрещен')


class BasePermission(RestBasePermissions):
    message = DEFAULT_MESSAGE


class IsNotAuthenticated(BaseException):
    def has_permission(self, request, view):
        return bool(request.user and not request.user.is_authenticated)


class IsOwner(BaseException):
    def __init__(self, attribute='user', **kwargs):
        self.user_attribute = attribute
        super().__init__(**kwargs)

    def __call__(self):
        return self.__class__(attribute=self.user_attribute)

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return bool(
            request.user
            and request.user.is_authenticated
            and operator.attrgetter(self.user_attribute)(obj) == request.user
        )
