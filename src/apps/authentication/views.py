from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.utils.translation import gettext_lazy as _
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.views import APIView, Response
from rest_framework_simplejwt.views import (
    TokenObtainPairView as BaseTokenObtainPairView,
)

from apps.core.exceptions import SingleValidationError
from apps.core.permissions import IsNotAuthenticated
from apps.users.models import User
from apps.users.serializers import PrivateUserSerailizer, UserRegisterSerializer

from . import backends, serializers, services


class TokenObtainPairView(BaseTokenObtainPairView):
    serializer_class = serializers.TokenObtainPairSerializer


class UserData(APIView):
    """ Getting current request user's data """

    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        return Response(PrivateUserSerailizer(request.user).data)


class Register(APIView):
    permission_classes = (IsNotAuthenticated,)

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            new_user = User.objects.create_user(
                username=serializer.validated_data['username'],
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password'],
            )

            token, created = Token.objects.get_or_create(user=new_user)

            return Response(
                {'token': token.key, 'data': PrivateUserSerailizer(new_user).data,}
            )


class SocialMediaAuth(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = serializers.SocialMediaSerializer
    backend_class = None

    def get_backend(self) -> backends.BaseSocialMediaBackend:
        assert self.backend_class
        return self.backend_class()

    def _auth_user(self, serializer: serializers.SocialMediaSerializer):
        user = self.get_backend().authenticate(
            self.request, serializer.validated_data['data'], create_user=True
        )
        if user is None:
            user_login_failed.send(
                sender=self.backend_class.__name__,
                credentials=serializer.validated_data['data'],
                request=self.request,
            )
            raise SingleValidationError(
                _('Данный пользователь не существуюет или деактивирован'),
            )
        user_logged_in.send(sender=user.__class__, request=self.request, user=user)
        return user

    def post(self, request: Request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(True)
        user = self._auth_user(serializer)

        return Response(services.get_user_tokens(user))


class TelegramAuth(SocialMediaAuth):
    backend_class = backends.TelegramBackend
