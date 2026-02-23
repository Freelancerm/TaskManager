from django.shortcuts import render
from django.views import View
from .models import Project, Task


class HomeView(View):
    def get(self, request):
        projects = Project.objects.filter(user=request.user)
        tasks = Task.objects.filter(user=request.user)
        return render(request, "home.html", {"projects": projects, "tasks": tasks})
