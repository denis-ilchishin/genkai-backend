from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

urlpatterns = (
    path('token/', views.TokenObtainPairView.as_view(), name='obtain-token'),
    path('refresh/', TokenRefreshView.as_view(), name='refresh-token'),
    path('user/', views.UserData.as_view(), name='user'),
    path('register/', views.Register.as_view(), name='register'),
    path('telegram/', views.TelegramAuth.as_view(), name='telegram'),
)
