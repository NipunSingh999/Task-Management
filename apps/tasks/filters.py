import django_filters
from django.utils import timezone
from .models import Task


class TaskFilter(django_filters.FilterSet):
    """
    Filter set for Task querying.
    Supports exact filtering by status and priority, as well as
    date ranges for due_date, and whether the task is overdue.
    """
    status = django_filters.ChoiceFilter(
        choices=Task.StatusChoices.choices,
        help_text="Filter by task status: pending, in_progress, or completed.",
    )
    priority = django_filters.ChoiceFilter(
        choices=Task.PriorityChoices.choices,
        help_text="Filter by task priority: low, medium, or high.",
    )
    due_date = django_filters.DateTimeFilter(
        field_name="due_date",
        lookup_expr="exact",
        help_text="Filter by exact due date and time (ISO format).",
    )
    due_date_after = django_filters.DateTimeFilter(
        field_name="due_date",
        lookup_expr="gte",
        help_text="Filter tasks due on or after this timestamp.",
    )
    due_date_before = django_filters.DateTimeFilter(
        field_name="due_date",
        lookup_expr="lte",
        help_text="Filter tasks due on or before this timestamp.",
    )
    is_overdue = django_filters.BooleanFilter(
        method="filter_is_overdue",
        help_text="Filter tasks that are overdue (true) or not overdue (false).",
    )

    class Meta:
        model = Task
        fields = ["status", "priority", "due_date"]

    def filter_is_overdue(self, queryset, name, value):
        now = timezone.now()
        if value is True:
            return queryset.filter(due_date__lt=now).exclude(status=Task.StatusChoices.COMPLETED)
        elif value is False:
            return queryset.exclude(due_date__lt=now, status__in=[Task.StatusChoices.PENDING, Task.StatusChoices.IN_PROGRESS])
        return queryset
