from django.urls import path
from .views import HomeView, TaskToggleDoneView

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("tasks/<int:pk>/toggle/", TaskToggleDoneView.as_view(), name="task-toggle"),
]
