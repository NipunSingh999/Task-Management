from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.utils import extend_schema

from .views import LoginView, ProfileView, RegisterView

# OpenAPI schema decoration for TokenRefreshView
DecoratedTokenRefreshView = extend_schema(
    tags=["Authentication"],
    summary="Refresh access token",
    description="Takes a valid refresh token and returns a new access token.",
)(TokenRefreshView)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("login/", LoginView.as_view(), name="auth-login"),
    path("refresh/", DecoratedTokenRefreshView.as_view(), name="auth-refresh"),
    path("profile/", ProfileView.as_view(), name="auth-profile"),
]
