from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class AuthenticationTests(APITestCase):
    """
    Test suite for TaskFlow authentication:
    - User registration
    - Username and email login
    - Token refresh
    - User profile management
    """

    def setUp(self):
        self.register_url = reverse("auth-register")
        self.login_url = reverse("auth-login")
        self.refresh_url = reverse("auth-refresh")
        self.profile_url = reverse("auth-profile")

        self.user_data = {
            "username": "alice",
            "email": "alice@example.com",
            "password": "StrongPassword123!",
            "password_confirm": "StrongPassword123!",
        }

        # Pre-created user for login tests
        self.existing_user = User.objects.create_user(
            username="bob",
            email="bob@example.com",
            password="BobPassword123!",
        )

    def test_register_user_success(self):
        """User can register with valid details and receives tokens."""
        response = self.client.post(self.register_url, self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("user", response.data)
        self.assertIn("tokens", response.data)
        self.assertEqual(response.data["user"]["username"], "alice")
        self.assertEqual(response.data["user"]["email"], "alice@example.com")
        self.assertTrue(User.objects.filter(username="alice").exists())

    def test_register_duplicate_username(self):
        """Registration fails if username already exists."""
        duplicate_data = self.user_data.copy()
        duplicate_data["username"] = "bob"
        response = self.client.post(self.register_url, duplicate_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_email(self):
        """Registration fails if email already exists."""
        duplicate_data = self.user_data.copy()
        duplicate_data["email"] = "bob@example.com"
        response = self.client.post(self.register_url, duplicate_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_password_mismatch(self):
        """Registration fails if passwords do not match."""
        mismatch_data = self.user_data.copy()
        mismatch_data["password_confirm"] = "DifferentPassword123!"
        response = self.client.post(self.register_url, mismatch_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_with_username_success(self):
        """User can log in using their username."""
        login_data = {
            "username": "bob",
            "password": "BobPassword123!",
        }
        response = self.client.post(self.login_url, login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("tokens", response.data)
        self.assertIn("access", response.data["tokens"])
        self.assertIn("refresh", response.data["tokens"])
        self.assertEqual(response.data["user"]["username"], "bob")

    def test_login_with_email_success(self):
        """User can log in using their email address instead of username."""
        login_data = {
            "username": "bob@example.com",
            "password": "BobPassword123!",
        }
        response = self.client.post(self.login_url, login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("tokens", response.data)
        self.assertEqual(response.data["user"]["username"], "bob")

    def test_login_invalid_password(self):
        """Login fails with invalid password."""
        login_data = {
            "username": "bob",
            "password": "WrongPassword123!",
        }
        response = self.client.post(self.login_url, login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_refresh_token_success(self):
        """Obtaining a new access token using a valid refresh token."""
        login_data = {
            "username": "bob",
            "password": "BobPassword123!",
        }
        login_res = self.client.post(self.login_url, login_data, format="json")
        refresh_token = login_res.data["tokens"]["refresh"]

        refresh_res = self.client.post(
            self.refresh_url, {"refresh": refresh_token}, format="json"
        )
        self.assertEqual(refresh_res.status_code, status.HTTP_200_OK)
        self.assertIn("access", refresh_res.data)

    def test_profile_requires_authentication(self):
        """Accessing profile without JWT token returns 401 Unauthorized."""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_authenticated_access(self):
        """Authenticated user can view their profile and task counters."""
        self.client.force_authenticate(user=self.existing_user)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "bob")
        self.assertEqual(response.data["email"], "bob@example.com")
        self.assertIn("total_tasks", response.data)
