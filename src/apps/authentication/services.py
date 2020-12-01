from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


def get_user_tokens(user):
    token = TokenObtainPairSerializer.get_token(user=user)
    return {'refresh': str(token), 'access': str(token.access_token)}
