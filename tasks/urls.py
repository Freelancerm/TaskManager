from django.urls import path
from .views import (
    HomeView,
    TaskCreateView,
    TaskToggleDoneView,
    TaskUpdateView,
    TaskDeleteView,
    ProjectCreateView,
    ProjectUpdateView,
    ProjectDeleteView,
)

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("tasks/new/", TaskCreateView.as_view(), name="task-create"),
    path("tasks/<int:pk>/toggle/", TaskToggleDoneView.as_view(), name="task-toggle"),
    path("tasks/<int:pk>/edit/", TaskUpdateView.as_view(), name="task-update"),
    path("tasks/<int:pk>/delete/", TaskDeleteView.as_view(), name="task-delete"),
    path("projects/new/", ProjectCreateView.as_view(), name="project-create"),
    path("projects/<int:pk>/edit/", ProjectUpdateView.as_view(), name="project-update"),
    path("projects/<int:pk>/delete/", ProjectDeleteView.as_view(), name="project-delete"),
]
