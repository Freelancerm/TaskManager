from django.urls import path
from .views import (
    HomeView,
    TaskListView,
    TaskCreateView,
    TaskToggleDoneView,
    TaskUpdateView,
    TaskDeleteView,
    ProjectCreateView,
    ProjectUpdateView,
    ProjectDeleteView,
    ProjectTasksView,
    ProjectTaskCreateView,
)

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("tasks/list/", TaskListView.as_view(), name="task-list"),
    path("tasks/new/", TaskCreateView.as_view(), name="task-create"),
    path("tasks/<int:pk>/toggle/", TaskToggleDoneView.as_view(), name="task-toggle"),
    path("tasks/<int:pk>/edit/", TaskUpdateView.as_view(), name="task-update"),
    path("tasks/<int:pk>/delete/", TaskDeleteView.as_view(), name="task-delete"),
    path("projects/new/", ProjectCreateView.as_view(), name="project-create"),
    path("projects/<int:pk>/edit/", ProjectUpdateView.as_view(), name="project-update"),
    path("projects/<int:pk>/delete/", ProjectDeleteView.as_view(), name="project-delete"),
    path("projects/<int:pk>/tasks/", ProjectTasksView.as_view(), name="project-tasks"),
    path(
        "projects/<int:pk>/tasks/new/",
        ProjectTaskCreateView.as_view(),
        name="project-task-create",
    ),
]
