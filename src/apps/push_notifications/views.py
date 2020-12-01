from rest_framework import generics, permissions
from rest_framework.request import Request
from rest_framework.response import Response

from . import serializers  # , services


class PushNotificationSubscription(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.PushNotificationSubscriptionSerializer

    def post(self, request: Request) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(True)
        serializer.save()
        return Response(serializer.data)
