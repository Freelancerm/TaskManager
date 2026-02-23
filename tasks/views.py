"""Views for task/project CRUD and HTMX partial rendering."""

import json

from django import forms
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F

from .models import Project, Task
from .forms import ProjectForm, TaskForm


class HomeView(LoginRequiredMixin, View):
    """Render the main dashboard with unassigned tasks and projects."""

    def get(self, request):
        projects = Project.objects.filter(user=request.user)
        tasks = Task.objects.filter(user=request.user, project__isnull=True).order_by(
            "is_done", "priority", F("due_date").asc(nulls_last=True), "-created_at"
        )
        return render(request, "home.html", {"projects": projects, "tasks": tasks})


class TaskToggleDoneView(LoginRequiredMixin, View):
    """Toggle task completion and return updated task row for HTMX."""

    def post(self, request, pk):
        task = get_object_or_404(Task, pk=pk, user=request.user)
        task.is_done = not task.is_done
        task.save(update_fields=["is_done"])
        response = render(request, "partials/task_item.html", {"task": task})
        trigger = (
            f"project-tasks-{task.project_id}"
            if task.project_id
            else "task-list-updated"
        )
        response.headers["HX-Trigger"] = trigger
        return response


class TaskListView(LoginRequiredMixin, View):
    """Return the unassigned task list partial for HTMX refresh."""

    def get(self, request):
        tasks = Task.objects.filter(user=request.user, project__isnull=True).order_by(
            "is_done", "priority", F("due_date").asc(nulls_last=True), "-created_at"
        )
        return render(request, "partials/task_list.html", {"tasks": tasks})


class TaskCreateView(LoginRequiredMixin, CreateView):
    """Create a task and return HTMX partials when requested."""

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
            trigger = (
                f"project-tasks-{task.project_id}"
                if task.project_id
                else "task-list-updated"
            )
            if task.project_id:
                blank_form = TaskForm(user=self.request.user)
                context = {
                    "form": blank_form,
                    "form_action": reverse("task-create"),
                    "form_title": "New task",
                    "submit_label": "Create",
                }
                response = render(self.request, self.template_name, context)
                response.headers["HX-Retarget"] = "#task-form-container"
                response.headers["HX-Reswap"] = "innerHTML"
            else:
                response = render(
                    self.request, "partials/task_item.html", {"task": task}
                )
            response.headers["HX-Trigger"] = trigger
            return response
        return redirect("home")

    def form_invalid(self, form):
        if self.request.htmx:
            response = render(
                self.request, self.template_name, self.get_context_data(form=form)
            )
            response.headers["HX-Retarget"] = "#task-form-container"
            response.headers["HX-Reswap"] = "innerHTML"
            return response
        return super().form_invalid(form)


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    """Update a task and emit HTMX triggers for list refreshes."""

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
        old_project_id = self.object.project_id
        task = form.save()
        if self.request.htmx:
            response = render(self.request, "partials/task_item.html", {"task": task})
            triggers = []
            if old_project_id:
                triggers.append(f"project-tasks-{old_project_id}")
            else:
                triggers.append("task-list-updated")
            if task.project_id and task.project_id != old_project_id:
                triggers.append(f"project-tasks-{task.project_id}")
            if task.project_id is None and task.project_id != old_project_id:
                triggers.append("task-list-updated")
            if len(triggers) == 1:
                response.headers["HX-Trigger"] = triggers[0]
            elif triggers:
                response.headers["HX-Trigger"] = json.dumps(
                    {name: "" for name in triggers}
                )
            return response
        return redirect("home")

    def form_invalid(self, form):
        if self.request.htmx:
            response = render(
                self.request, self.template_name, self.get_context_data(form=form)
            )
            response.headers["HX-Retarget"] = "#task-form-container"
            response.headers["HX-Reswap"] = "innerHTML"
            return response
        return super().form_invalid(form)


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a task and emit HTMX triggers for list refreshes."""

    model = Task
    success_url = reverse_lazy("home")
    http_method_names = ["post", "delete"]

    def __init__(self, **kwargs):
        super().__init__(kwargs)
        self.object = None

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        project_id = self.object.project_id
        self.object.delete()
        is_htmx = (
            bool(getattr(request, "htmx", False))
            or request.headers.get("HX-Request") == "true"
        )
        if is_htmx:
            response = HttpResponse("")
            response.headers["HX-Trigger"] = (
                f"project-tasks-{project_id}" if project_id else "task-list-updated"
            )
            return response
        return redirect(self.get_success_url())

    def post(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)


class ProjectCreateView(LoginRequiredMixin, CreateView):
    """Create a project and return HTMX partials when requested."""

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
            return render(
                self.request, self.template_name, self.get_context_data(form=form)
            )
        return super().form_invalid(form)


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    """Update a project and return HTMX partials when requested."""

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
            return render(
                self.request, self.template_name, self.get_context_data(form=form)
            )
        return super().form_invalid(form)


class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a project and emit HTMX triggers for list refreshes."""

    model = Project
    success_url = reverse_lazy("home")
    http_method_names = ["post", "delete"]

    def __init__(self, **kwargs):
        super().__init__(kwargs)
        self.object = None

    def get_queryset(self):
        return Project.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        is_htmx = (
            bool(getattr(request, "htmx", False))
            or request.headers.get("HX-Request") == "true"
        )
        if is_htmx:
            response = HttpResponse("")
            response.headers["HX-Trigger"] = "project-list-changed"
            return response
        return redirect(self.get_success_url())

    def post(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)


class ProjectTasksView(LoginRequiredMixin, View):
    """Render tasks for a project along with inline task form."""

    def get(self, request, pk):
        project = get_object_or_404(Project, pk=pk, user=request.user)
        tasks = Task.objects.filter(user=request.user, project=project).order_by(
            "is_done", "priority", F("due_date").asc(nulls_last=True), "-created_at"
        )
        form = TaskForm(user=request.user, initial={"project": project})
        form.fields["project"].widget = forms.HiddenInput()
        return render(
            request,
            "partials/project_tasks.html",
            {"project": project, "tasks": tasks, "form": form},
        )


class ProjectTaskCreateView(LoginRequiredMixin, View):
    """Create a task directly within a project and re-render its block."""

    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk, user=request.user)
        form = TaskForm(request.POST, user=request.user)
        form.fields["project"].widget = forms.HiddenInput()
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.project = project
            task.save()
            tasks = Task.objects.filter(user=request.user, project=project).order_by(
                "is_done", "priority", F("due_date").asc(nulls_last=True), "-created_at"
            )
            blank_form = TaskForm(user=request.user, initial={"project": project})
            blank_form.fields["project"].widget = forms.HiddenInput()
            return render(
                request,
                "partials/project_tasks.html",
                {"project": project, "tasks": tasks, "form": blank_form},
            )
        tasks = Task.objects.filter(user=request.user, project=project).order_by(
            "is_done", "priority", F("due_date").asc(nulls_last=True), "-created_at"
        )
        return render(
            request,
            "partials/project_tasks.html",
            {"project": project, "tasks": tasks, "form": form},
        )
