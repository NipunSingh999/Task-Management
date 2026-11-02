from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    LoginSerializer,
    RegisterSerializer,
    UserProfileSerializer,
)

User = get_user_model()


@extend_schema(
    tags=["Authentication"],
    summary="Register a new user",
    description="Registers a new user with username, unique email, and password. Returns user info and initial JWT tokens.",
    responses={
        201: OpenApiResponse(
            response=UserProfileSerializer,
            description="User registered successfully."
        ),
        400: OpenApiResponse(description="Validation error (e.g. duplicate email/username, password mismatch)."),
    },
)
class RegisterView(generics.CreateAPIView):
    """
    Register a new user account.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "User registered successfully.",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "created_at": user.created_at,
                },
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            },
            status=status.HTTP_201_CREATED,
        )


@extend_schema(
    tags=["Authentication"],
    summary="User login",
    description="Authenticate with username (or email) and password to obtain JWT access and refresh tokens.",
    request=LoginSerializer,
    responses={
        200: OpenApiResponse(description="Login successful, tokens returned."),
        400: OpenApiResponse(description="Invalid credentials or inactive account."),
    },
)
class LoginView(generics.GenericAPIView):
    """
    Obtain JWT access and refresh tokens using username/email and password.
    """
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


@extend_schema(
    tags=["Authentication"],
    summary="Get or update user profile",
    description="Retrieve or partially update the authenticated user's profile and task summary statistics.",
    responses={
        200: UserProfileSerializer,
        401: OpenApiResponse(description="Authentication credentials were not provided or are invalid."),
    },
)
class ProfileView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update the authenticated user's profile.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
