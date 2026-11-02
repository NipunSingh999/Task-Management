from datetime import timedelta
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.tasks.models import Task

User = get_user_model()


class TaskAPITests(APITestCase):
    """
    Comprehensive test suite for Task CRUD, permissions, filtering,
    search, pagination, and status management.
    """

    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user_one",
            email="user1@example.com",
            password="Password123!",
        )
        self.user2 = User.objects.create_user(
            username="user_two",
            email="user2@example.com",
            password="Password123!",
        )

        self.list_url = reverse("task-list")

        # Create tasks for user1
        self.task1 = Task.objects.create(
            user=self.user1,
            title="Complete CS assignment",
            description="Finish the Django REST API assignment",
            status=Task.StatusChoices.PENDING,
            priority=Task.PriorityChoices.HIGH,
            due_date=timezone.now() + timedelta(days=2),
        )
        self.task2 = Task.objects.create(
            user=self.user1,
            title="Buy groceries",
            description="Milk, eggs, and bread",
            status=Task.StatusChoices.COMPLETED,
            priority=Task.PriorityChoices.LOW,
            due_date=timezone.now() + timedelta(days=1),
        )
        self.task3 = Task.objects.create(
            user=self.user1,
            title="Code review for pull request",
            description="Review authentication logic",
            status=Task.StatusChoices.IN_PROGRESS,
            priority=Task.PriorityChoices.MEDIUM,
            due_date=timezone.now() + timedelta(days=3),
        )

        # Create a task for user2 to verify user isolation
        self.user2_task = Task.objects.create(
            user=self.user2,
            title="User 2 Secret Task",
            description="Private task for user 2",
            status=Task.StatusChoices.PENDING,
            priority=Task.PriorityChoices.HIGH,
        )

    def test_unauthenticated_requests_denied(self):
        """Unauthenticated requests must be rejected with 401 Unauthorized."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.post(self.list_url, {"title": "Test"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_task_success(self):
        """Authenticated user can create a task and is set as owner."""
        self.client.force_authenticate(user=self.user1)
        payload = {
            "title": "Prepare presentation slides",
            "description": "Create slides for sprint demo",
            "status": "pending",
            "priority": "high",
            "due_date": (timezone.now() + timedelta(days=5)).isoformat(),
        }
        response = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], payload["title"])
        self.assertEqual(response.data["user_id"], self.user1.id)
        self.assertEqual(response.data["status"], "pending")
        self.assertEqual(response.data["status_display"], "Pending")
        self.assertEqual(response.data["priority"], "high")

    def test_create_task_empty_title_fails(self):
        """Creating a task with an empty or whitespace title returns 400 Bad Request."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.list_url, {"title": "   "}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_isolation_listing(self):
        """Users can only view their own tasks; other users' tasks are never returned."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        task_titles = [t["title"] for t in response.data["results"]]
        self.assertIn("Complete CS assignment", task_titles)
        self.assertIn("Buy groceries", task_titles)
        self.assertNotIn("User 2 Secret Task", task_titles)

    def test_retrieve_task_detail_and_isolation(self):
        """User can retrieve their task, but accessing another user's task returns 404."""
        self.client.force_authenticate(user=self.user1)
        detail_url = reverse("task-detail", kwargs={"pk": self.task1.id})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.task1.title)

        # Attempt to access user2's task
        other_detail_url = reverse("task-detail", kwargs={"pk": self.user2_task.id})
        forbidden_response = self.client.get(other_detail_url)
        self.assertEqual(forbidden_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_task_put(self):
        """Full update (PUT) modifies all task fields."""
        self.client.force_authenticate(user=self.user1)
        detail_url = reverse("task-detail", kwargs={"pk": self.task1.id})
        payload = {
            "title": "Complete CS assignment - Updated",
            "description": "Updated description with more details",
            "status": "in_progress",
            "priority": "medium",
        }
        response = self.client.put(detail_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Complete CS assignment - Updated")
        self.assertEqual(response.data["status"], "in_progress")

    def test_partial_update_task_patch(self):
        """Partial update (PATCH) modifies only specified fields."""
        self.client.force_authenticate(user=self.user1)
        detail_url = reverse("task-detail", kwargs={"pk": self.task1.id})
        response = self.client.patch(
            detail_url, {"status": "completed"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "completed")
        self.assertEqual(response.data["status_display"], "Completed")

    def test_update_other_user_task_fails(self):
        """Users cannot update other users' tasks (returns 404)."""
        self.client.force_authenticate(user=self.user1)
        other_url = reverse("task-detail", kwargs={"pk": self.user2_task.id})
        response = self.client.patch(other_url, {"title": "Hacked"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_task_success_and_isolation(self):
        """User can delete their own task (204 No Content), but cannot delete others' tasks."""
        self.client.force_authenticate(user=self.user1)
        detail_url = reverse("task-detail", kwargs={"pk": self.task1.id})
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(id=self.task1.id).exists())

        # Attempt to delete user2's task
        other_url = reverse("task-detail", kwargs={"pk": self.user2_task.id})
        forbidden_del = self.client.delete(other_url)
        self.assertEqual(forbidden_del.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Task.objects.filter(id=self.user2_task.id).exists())

    def test_filter_by_status(self):
        """Filtering tasks by ?status=... returns only matching tasks."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f"{self.list_url}?status=completed")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "Buy groceries")

    def test_filter_by_priority(self):
        """Filtering tasks by ?priority=... returns only matching tasks."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f"{self.list_url}?priority=high")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "Complete CS assignment")

    def test_search_tasks_by_title_and_description(self):
        """Search by query parameter ?search=... matches title or description."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f"{self.list_url}?search=assignment")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "Complete CS assignment")

    def test_ordering_and_pagination(self):
        """Verify sorting by created_at and custom page size pagination."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f"{self.list_url}?ordering=created_at&page_size=2")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertIsNotNone(response.data["next"])

    def test_task_summary_endpoint(self):
        """GET /api/tasks/summary/ returns aggregated status and priority counts."""
        self.client.force_authenticate(user=self.user1)
        summary_url = reverse("task-summary")
        response = self.client.get(summary_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total"], 3)
        self.assertEqual(response.data["status"]["pending"], 1)
        self.assertEqual(response.data["status"]["completed"], 1)
        self.assertEqual(response.data["status"]["in_progress"], 1)
        self.assertEqual(response.data["priority"]["high"], 1)
        self.assertEqual(response.data["priority"]["medium"], 1)
        self.assertEqual(response.data["priority"]["low"], 1)
