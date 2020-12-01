from django.utils.translation import gettext_lazy as _
from rest_framework.permissions import BasePermission

# class UnsafeIsAuthenticated(BasePermission):
#     message = _('У Вас нет доступа к данному объекту')

#     def has_object_permission(self, request, view, obj):
#         return bool(request.user and request.user.is_authenticated and obj.user == request.user)
