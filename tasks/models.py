from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import F


class Project(models.Model):
    """User-owned project for grouping tasks."""

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="projects")
    name = models.CharField(max_length=120)

    def __str__(self):
        return self.name


class TaskQuerySet(models.QuerySet):
    def for_user(self, user):
        return self.filter(user=user)

    def unassigned(self, user):
        return self.for_user(user).filter(project__isnull=True)

    def in_project(self, project, user):
        return self.for_user(user).filter(project=project)

    def ordered(self):
        return self.order_by(
            "is_done",
            "priority",
            F("due_date").asc(nulls_last=True),
            "-created_at",
        )


class Task(models.Model):
    """User-owned task with optional project, priority, and due date."""

    PRIORITY_HIGH = 1
    PRIORITY_MEDIUM = 2
    PRIORITY_LOW = 3
    PRIORITY_CHOICES = [
        (PRIORITY_HIGH, "High"),
        (PRIORITY_MEDIUM, "Medium"),
        (PRIORITY_LOW, "Low"),
    ]
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="tasks")
    priority = models.PositiveSmallIntegerField(choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=160)
    description = models.TextField(blank=True)

    due_date = models.DateField(blank=True, null=True)
    is_done = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = TaskQuerySet.as_manager()

    class Meta:
        ordering = ["is_done", "priority", "due_date", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "project", "title"], name="uniq_task_title_per_project"
            )
        ]

    def __str__(self):
        return self.title
