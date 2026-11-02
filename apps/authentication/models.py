from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model for TaskFlow.
    Extends Django's AbstractUser to enforce unique emails and
    record explicit created_at and updated_at timestamps.
    """
    email = models.EmailField(
        unique=True,
        verbose_name="Email Address",
        error_messages={
            "unique": "A user with that email already exists.",
        },
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    REQUIRED_FIELDS = ["email"]

    class Meta:
        db_table = "users"
        ordering = ["-created_at"]
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.username} <{self.email}>"

    @property
    def total_tasks(self):
        return self.tasks.count()

    @property
    def pending_tasks(self):
        return self.tasks.filter(status="pending").count()

    @property
    def in_progress_tasks(self):
        return self.tasks.filter(status="in_progress").count()

    @property
    def completed_tasks(self):
        return self.tasks.filter(status="completed").count()
