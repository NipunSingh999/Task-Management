from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import TaskFilter
from .models import Task
from .permissions import IsOwner
from .serializers import TaskSerializer


@extend_schema_view(
    list=extend_schema(
        tags=["Tasks"],
        summary="List user tasks",
        description="Retrieve a paginated list of tasks belonging to the authenticated user. Supports status/priority filtering, text search, and sorting.",
    ),
    create=extend_schema(
        tags=["Tasks"],
        summary="Create a new task",
        description="Creates a new task associated with the authenticated user.",
        responses={
            201: TaskSerializer,
            400: OpenApiResponse(description="Validation error."),
        },
    ),
    retrieve=extend_schema(
        tags=["Tasks"],
        summary="Retrieve task details",
        description="Retrieve details of a specific task owned by the authenticated user.",
        responses={
            200: TaskSerializer,
            404: OpenApiResponse(description="Task not found."),
        },
    ),
    update=extend_schema(
        tags=["Tasks"],
        summary="Update a task",
        description="Update all fields of an existing task owned by the authenticated user.",
        responses={
            200: TaskSerializer,
            400: OpenApiResponse(description="Validation error."),
            404: OpenApiResponse(description="Task not found."),
        },
    ),
    partial_update=extend_schema(
        tags=["Tasks"],
        summary="Partially update a task",
        description="Update one or more fields (e.g. status, priority, title, due_date) of an existing task.",
        responses={
            200: TaskSerializer,
            400: OpenApiResponse(description="Validation error."),
            404: OpenApiResponse(description="Task not found."),
        },
    ),
    destroy=extend_schema(
        tags=["Tasks"],
        summary="Delete a task",
        description="Permanently delete a task owned by the authenticated user.",
        responses={
            204: OpenApiResponse(description="Task successfully deleted."),
            404: OpenApiResponse(description="Task not found."),
        },
    ),
)
class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing tasks.
    Enforces user isolation: users can only view, edit, and delete their own tasks.
    """
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TaskFilter
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "updated_at", "due_date", "priority", "status", "title"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Task.objects.none()
        return Task.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(
        tags=["Tasks"],
        summary="Get task status & priority summary",
        description="Returns an aggregated summary count of tasks by status and priority for the authenticated user.",
        responses={200: OpenApiResponse(description="Aggregated task statistics.")},
    )
    @action(detail=False, methods=["get"], url_path="summary")
    def summary(self, request):
        qs = self.get_queryset()
        data = {
            "total": qs.count(),
            "status": {
                "pending": qs.filter(status=Task.StatusChoices.PENDING).count(),
                "in_progress": qs.filter(status=Task.StatusChoices.IN_PROGRESS).count(),
                "completed": qs.filter(status=Task.StatusChoices.COMPLETED).count(),
            },
            "priority": {
                "low": qs.filter(priority=Task.PriorityChoices.LOW).count(),
                "medium": qs.filter(priority=Task.PriorityChoices.MEDIUM).count(),
                "high": qs.filter(priority=Task.PriorityChoices.HIGH).count(),
            },
            "overdue": [t.id for t in qs if t.is_overdue],
        }
        return Response(data, status=status.HTTP_200_OK)
