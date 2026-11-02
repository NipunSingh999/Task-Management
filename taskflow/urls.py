"""
URL configuration for TaskFlow project.
"""
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([AllowAny])
def api_root(request):
    """
    API Root providing discoverability and status of the TaskFlow service.
    """
    return Response({
        "name": "TaskFlow — Task Management REST API",
        "version": "1.0.0",
        "status": "online",
        "documentation": {
            "swagger_ui": request.build_absolute_uri("/api/docs/"),
            "redoc": request.build_absolute_uri("/api/redoc/"),
            "openapi_schema": request.build_absolute_uri("/api/schema/"),
        },
        "endpoints": {
            "authentication": {
                "register": request.build_absolute_uri("/api/auth/register/"),
                "login": request.build_absolute_uri("/api/auth/login/"),
                "refresh": request.build_absolute_uri("/api/auth/refresh/"),
                "profile": request.build_absolute_uri("/api/auth/profile/"),
            },
            "tasks": request.build_absolute_uri("/api/tasks/"),
        },
    })


urlpatterns = [
    # Administration
    path("admin/", admin.site.urls),

    # Service Root
    path("", api_root, name="api-root"),
    path("api/", api_root, name="api-root-v1"),

    # API Documentation (drf-spectacular)
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),

    # Application Endpoints
    path("api/auth/", include("apps.authentication.urls")),
    path("api/tasks/", include("apps.tasks.urls")),
]
