from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q


class EmailOrUsernameModelBackend(ModelBackend):
    """
    Custom authentication backend that allows users to authenticate
    using either their username or their email address.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        user_model = get_user_model()
        if username is None:
            username = kwargs.get(user_model.USERNAME_FIELD) or kwargs.get("email")

        if not username or not password:
            return None

        try:
            # Match either username or email (case-insensitive)
            user = user_model.objects.get(
                Q(username__iexact=username) | Q(email__iexact=username)
            )
        except (user_model.DoesNotExist, user_model.MultipleObjectsReturned):
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None
