from django.utils.translation import gettext_lazy as _
from rest_framework import generics, permissions
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsOwner

from . import models, serializers


class NotificationDelete(generics.DestroyAPIView):
    permission_classes = (permissions.IsAuthenticated, IsOwner)
    queryset = models.Notification.objects.enabled()
    serializer_class = serializers.NotificationSerializer

    def delete(self, request: Request, **kwargs) -> Response:

        return Response(
            {'notifications_count': request.user.get_not_seen_notifications_count()}
        )


class NotificationSeen(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated, IsOwner)
    queryset = models.Notification.objects.enabled()
    serializer_class = serializers.NotificationSerializer

    def post(self, request: Request, **kwargs) -> Response:
        notification = self.get_object()
        notification.seen = True
        notification.save()

        return Response(
            {'notifications_count': request.user.get_not_seen_notifications_count()}
        )


class NotificationSeenAll(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request: Request) -> Response:
        request.user.notifications.update(seen=True)
        return Response(
            {'notifications_count': request.user.get_not_seen_notifications_count()}
        )


class NotificationDeleteAll(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def delete(self, request: Request) -> Response:
        request.user.notifications.all().delete()
        return Response(
            {'notifications_count': request.user.get_not_seen_notifications_count()}
        )


class NotificationDeleteSelected(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.NotificationIdsSerializer

    def post(self, request: Request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(True)
        not_exist = []
        to_delete = []

        for notification_id in serializer.validated_data['ids']:
            exists = request.user.notifications.filter(pk=notification_id).exists()
            if exists:
                to_delete.append(notification_id)
            else:
                not_exist.append(notification_id)

        if len(to_delete):
            request.user.notifications.filter(pk__in=to_delete).delete()

        return Response(
            {
                'deleted': to_delete,
                'not_exist': not_exist,
                'notifications_count': request.user.get_not_seen_notifications_count(),
            }
        )


class NotificationSeenSelected(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.NotificationIdsSerializer

    def post(self, request: Request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(True)
        not_exist = []
        to_set_as_seen = []

        for notification_id in serializer.validated_data['ids']:
            exists = self.request.user.notifications.filter(pk=notification_id).exists()
            if exists:
                to_set_as_seen.append(notification_id)
            else:
                not_exist.append(notification_id)

        if len(to_set_as_seen):
            self.request.user.notifications.filter(pk__in=to_set_as_seen).update(
                seen=True
            )

        return Response(
            {
                'seen': to_set_as_seen,
                'not_exist': not_exist,
                'notifications_count': self.request.user.get_not_seen_notifications_count(),
            }
        )


class NotificationList(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.NotificationSerializer

    def get_queryset(self):
        return self.request.user.notifications.all()
