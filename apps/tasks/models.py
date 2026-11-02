from django.conf import settings
from django.db import models
from django.utils import timezone


class Task(models.Model):
    """
    Task model representing an item created and managed by an authenticated user.
    """

    class StatusChoices(models.TextChoices):
        PENDING = "pending", "Pending"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"

    class PriorityChoices(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tasks",
        verbose_name="Owner",
        help_text="User who owns this task.",
    )
    title = models.CharField(
        max_length=255,
        verbose_name="Title",
        help_text="Short summary or title of the task.",
    )
    description = models.TextField(
        blank=True,
        default="",
        verbose_name="Description",
        help_text="Detailed description of the task requirements.",
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
        db_index=True,
        verbose_name="Status",
        help_text="Current state of the task (pending, in_progress, completed).",
    )
    priority = models.CharField(
        max_length=20,
        choices=PriorityChoices.choices,
        default=PriorityChoices.MEDIUM,
        db_index=True,
        verbose_name="Priority",
        help_text="Importance level of the task (low, medium, high).",
    )
    due_date = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Due Date",
        help_text="Deadline or target completion date and time.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="Created At",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At",
    )

    class Meta:
        db_table = "tasks"
        ordering = ["-created_at"]
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["user", "priority"]),
            models.Index(fields=["user", "due_date"]),
        ]

    def __str__(self):
        return f"[{self.get_status_display()}] {self.title} ({self.user.username})"

    @property
    def is_overdue(self):
        """Check if the task has passed its due date without being completed."""
        if self.due_date and self.status != self.StatusChoices.COMPLETED:
            return timezone.now() > self.due_date
        return False
