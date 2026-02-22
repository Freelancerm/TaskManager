from django.shortcuts import render
from django.views import View
from .models import Project, Task


class HomeView(View):
    def get(self, request):
        print(request.user.id)
        print(request.__dict__)
        projects = Project.objects.filter(user=request.user.id)
        tasks = Task.objects.filter(user=request.user.id)
        print(tasks)
        return render(request, "home.html", {"projects": projects, "tasks": tasks})
