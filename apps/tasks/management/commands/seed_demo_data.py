from datetime import timedelta
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.tasks.models import Task

User = get_user_model()


class Command(BaseCommand):
    help = "Seeds the database with demo users and realistic tasks for testing and Swagger exploration."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding demo data..."))

        # Create or update Demo User
        demo_user, created = User.objects.get_or_create(
            username="demo_user",
            defaults={"email": "demo@taskflow.dev"},
        )
        demo_user.set_password("DemoPassword123!")
        demo_user.save()

        # Create or update Second Demo User for isolation tests
        dev_user, _ = User.objects.get_or_create(
            username="dev_alex",
            defaults={"email": "alex@taskflow.dev"},
        )
        dev_user.set_password("AlexPassword123!")
        dev_user.save()

        # Clear existing demo tasks for idempotency
        Task.objects.filter(user__in=[demo_user, dev_user]).delete()

        now = timezone.now()

        tasks_demo_user = [
            {
                "title": "Design REST API schema for TaskFlow",
                "description": "Finalize OpenAPI 3.0 / Swagger specification with all endpoints, request bodies, and responses.",
                "status": Task.StatusChoices.COMPLETED,
                "priority": Task.PriorityChoices.HIGH,
                "due_date": now - timedelta(days=1),
            },
            {
                "title": "Implement JWT authentication and user profile",
                "description": "Configure SimpleJWT, email/username login backend, registration, and profile endpoints.",
                "status": Task.StatusChoices.COMPLETED,
                "priority": Task.PriorityChoices.HIGH,
                "due_date": now - timedelta(hours=6),
            },
            {
                "title": "Build Task CRUD viewset with ownership isolation",
                "description": "Support GET, POST, PUT, PATCH, DELETE operations restricted strictly to owning user.",
                "status": Task.StatusChoices.IN_PROGRESS,
                "priority": Task.PriorityChoices.HIGH,
                "due_date": now + timedelta(days=1),
            },
            {
                "title": "Add advanced filtering, search, and pagination",
                "description": "Filter by status and priority, search title and description, order by creation or deadline.",
                "status": Task.StatusChoices.IN_PROGRESS,
                "priority": Task.PriorityChoices.MEDIUM,
                "due_date": now + timedelta(days=2),
            },
            {
                "title": "Prepare Dockerfile and docker-compose deployment",
                "description": "Package Django app with PostgreSQL container and automated database migrations.",
                "status": Task.StatusChoices.PENDING,
                "priority": Task.PriorityChoices.MEDIUM,
                "due_date": now + timedelta(days=3),
            },
            {
                "title": "Write comprehensive unit and integration tests",
                "description": "Ensure 100% coverage on authentication, permissions, filtering, and edge cases.",
                "status": Task.StatusChoices.PENDING,
                "priority": Task.PriorityChoices.LOW,
                "due_date": now + timedelta(days=4),
            },
        ]

        tasks_dev_user = [
            {
                "title": "Setup CI/CD pipeline on GitHub Actions",
                "description": "Run automated test suites and linting on every pull request.",
                "status": Task.StatusChoices.PENDING,
                "priority": Task.PriorityChoices.HIGH,
                "due_date": now + timedelta(days=5),
            },
            {
                "title": "Research Redis caching for task statistics",
                "description": "Evaluate caching user profile task counters with Redis.",
                "status": Task.StatusChoices.PENDING,
                "priority": Task.PriorityChoices.LOW,
                "due_date": now + timedelta(days=7),
            },
        ]

        for t in tasks_demo_user:
            Task.objects.create(user=demo_user, **t)

        for t in tasks_dev_user:
            Task.objects.create(user=dev_user, **t)

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully seeded {len(tasks_demo_user)} tasks for '{demo_user.username}' "
                f"and {len(tasks_dev_user)} tasks for '{dev_user.username}'."
            )
        )
        self.stdout.write(
            self.style.SUCCESS("Demo credentials: username='demo_user', password='DemoPassword123!'")
        )
