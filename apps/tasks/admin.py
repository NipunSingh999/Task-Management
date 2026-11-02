from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Admin configuration for Task model."""
    list_display = ("title", "user", "status", "priority", "due_date", "created_at")
    list_filter = ("status", "priority", "created_at", "due_date")
    search_fields = ("title", "description", "user__username", "user__email")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")
    list_select_related = ("user",)
