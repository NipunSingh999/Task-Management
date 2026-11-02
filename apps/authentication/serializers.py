from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving and updating user profile details.
    Includes task metrics (total, pending, in_progress, completed).
    """
    total_tasks = serializers.ReadOnlyField()
    pending_tasks = serializers.ReadOnlyField()
    in_progress_tasks = serializers.ReadOnlyField()
    completed_tasks = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "created_at",
            "total_tasks",
            "pending_tasks",
            "in_progress_tasks",
            "completed_tasks",
        ]
        read_only_fields = [
            "id",
            "username",
            "created_at",
            "total_tasks",
            "pending_tasks",
            "in_progress_tasks",
            "completed_tasks",
        ]


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for new user registration.
    Validates username uniqueness, email uniqueness, password confirmation,
    and Django's standard password complexity rules.
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
        validators=[validate_password],
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "password_confirm", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate_email(self, value):
        normalized_email = value.lower().strip()
        if User.objects.filter(email__iexact=normalized_email).exists():
            raise serializers.ValidationError("A user with this email address already exists.")
        return normalized_email

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Password fields do not match."}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for authenticating users via username OR email and password.
    Returns access and refresh JWT tokens upon successful authentication.
    """
    username = serializers.CharField(
        required=True,
        help_text="Enter your registered username or email address.",
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={"input_type": "password"},
        help_text="Enter your password.",
    )

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        user = authenticate(username=username, password=password)

        if not user:
            raise serializers.ValidationError(
                "Invalid credentials. Please verify your username/email and password."
            )

        if not user.is_active:
            raise serializers.ValidationError("This user account is inactive.")

        refresh = RefreshToken.for_user(user)

        return {
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
        }
