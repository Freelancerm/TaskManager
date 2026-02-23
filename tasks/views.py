from django.shortcuts import get_object_or_404, render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Project, Task


class HomeView(View):
    def get(self, request):
        projects = Project.objects.filter(user=request.user)
        tasks = Task.objects.filter(user=request.user)
        return render(request, "home.html", {"projects": projects, "tasks": tasks})


class TaskToggleDoneView(LoginRequiredMixin, View):
    def post(self, request, pk):
        task = get_object_or_404(Task, pk=pk, user=request.user)
        task.is_done = not task.is_done
        task.save(update_fields=["is_done"])
        return render(request, "partials/task_item.html", {"task": task})
