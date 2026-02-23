from django.urls import path
from .views import (
    HomeView,
    TaskToggleDoneView,
    ProjectCreateView,
    ProjectUpdateView,
    ProjectDeleteView,
)

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("tasks/<int:pk>/toggle/", TaskToggleDoneView.as_view(), name="task-toggle"),
    path("projects/new/", ProjectCreateView.as_view(), name="project-create"),
    path("projects/<int:pk>/edit/", ProjectUpdateView.as_view(), name="project-update"),
    path("projects/<int:pk>/delete/", ProjectDeleteView.as_view(), name="project-delete"),
]
