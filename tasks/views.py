from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Project, Task
from .forms import ProjectForm, TaskForm


class HomeView(View):
    def get(self, request):
        projects = Project.objects.filter(user=request.user)
        tasks = Task.objects.filter(user=request.user, project__isnull=True)
        return render(request, "home.html", {"projects": projects, "tasks": tasks})


class TaskToggleDoneView(LoginRequiredMixin, View):
    def post(self, request, pk):
        task = get_object_or_404(Task, pk=pk, user=request.user)
        task.is_done = not task.is_done
        task.save(update_fields=["is_done"])
        return render(request, "partials/task_item.html", {"task": task})


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = "partials/task_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_action"] = reverse("task-create")
        context["form_title"] = "New task"
        context["submit_label"] = "Create"
        return context

    def form_valid(self, form):
        task = form.save(commit=False)
        task.user = self.request.user
        task.save()
        if self.request.htmx:
            if task.project_id is None:
                return render(self.request, "partials/task_item.html", {"task": task})
            return HttpResponse("")
        return redirect("home")

    def form_invalid(self, form):
        if self.request.htmx:
            return render(self.request, self.template_name, self.get_context_data(form=form))
        return super().form_invalid(form)


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "partials/task_form.html"

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_action"] = reverse("task-update", args=[self.object.pk])
        context["form_title"] = "Edit task"
        context["submit_label"] = "Save"
        return context

    def form_valid(self, form):
        task = form.save()
        if self.request.htmx:
            return render(self.request, "partials/task_item.html", {"task": task})
        return redirect("home")

    def form_invalid(self, form):
        if self.request.htmx:
            return render(self.request, self.template_name, self.get_context_data(form=form))
        return super().form_invalid(form)


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    success_url = reverse_lazy("home")
    http_method_names = ["post", "delete"]

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        is_htmx = bool(getattr(request, "htmx", False)) or request.headers.get(
            "HX-Request"
        ) == "true"
        if is_htmx:
            return HttpResponse("")
        return redirect(self.get_success_url())

    def post(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "partials/project_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_action"] = reverse("project-create")
        context["form_title"] = "New project"
        context["submit_label"] = "Create"
        return context

    def form_valid(self, form):
        project = form.save(commit=False)
        project.user = self.request.user
        project.save()
        if self.request.htmx:
            response = render(
                self.request, "partials/project_item.html", {"project": project}
            )
            response.headers["HX-Trigger"] = "project-list-changed"
            return response
        return redirect("home")

    def form_invalid(self, form):
        if self.request.htmx:
            return render(self.request, self.template_name, self.get_context_data(form=form))
        return super().form_invalid(form)


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = "partials/project_form.html"

    def get_queryset(self):
        return Project.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_action"] = reverse("project-update", args=[self.object.pk])
        context["form_title"] = "Edit project"
        context["submit_label"] = "Save"
        return context

    def form_valid(self, form):
        project = form.save()
        if self.request.htmx:
            response = render(
                self.request, "partials/project_item.html", {"project": project}
            )
            response.headers["HX-Trigger"] = "project-list-changed"
            return response
        return redirect("home")

    def form_invalid(self, form):
        if self.request.htmx:
            return render(self.request, self.template_name, self.get_context_data(form=form))
        return super().form_invalid(form)


class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Project
    success_url = reverse_lazy("home")
    http_method_names = ["post", "delete"]

    def get_queryset(self):
        return Project.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        is_htmx = bool(getattr(request, "htmx", False)) or request.headers.get(
            "HX-Request"
        ) == "true"
        if is_htmx:
            response = HttpResponse("")
            response.headers["HX-Trigger"] = "project-list-changed"
            return response
        return redirect(self.get_success_url())

    def post(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)


class ProjectTasksView(LoginRequiredMixin, View):
    def get(self, request, pk):
        project = get_object_or_404(Project, pk=pk, user=request.user)
        tasks = Task.objects.filter(user=request.user, project=project)
        return render(
            request,
            "partials/project_tasks.html",
            {"project": project, "tasks": tasks},
        )
