from django import forms
from django.utils import timezone

from .models import Project, Task


class TaskForm(forms.ModelForm):
    """Task form with per-user project filtering and validation rules."""

    class Meta:
        model = Task
        fields = ["title", "description", "priority", "due_date", "project"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Start typing here to create a task...",
                    "required": True,
                }
            ),
            "description": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "Description"}
            ),
            "priority": forms.Select(attrs={"class": "form-select", "required": True}),
            "due_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "project": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields["project"].queryset = Project.objects.filter(user=user)
            self.user = user
        else:
            self.user = None
        self.fields["due_date"].widget.attrs["min"] = timezone.localdate().isoformat()

    def clean_due_date(self):
        """Disallow due dates in the past."""
        due_date = self.cleaned_data.get("due_date")
        if due_date and due_date < timezone.localdate():
            raise forms.ValidationError("Due date cannot be in the past.")
        return due_date

    def clean(self):
        """Ensure task title is unique within the same project for a user."""
        cleaned_data = super().clean()
        title = cleaned_data.get("title")
        project = cleaned_data.get("project")
        if not title or self.user is None:
            return cleaned_data
        exists = (
            Task.objects.filter(user=self.user, project=project, title=title)
            .exclude(pk=self.instance.pk)
            .exists()
        )
        if exists:
            self.add_error("title", "Task with this title already exists in this project.")
        return cleaned_data


class ProjectForm(forms.ModelForm):
    """Project form."""

    class Meta:
        model = Project
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Project name",
                    "required": True,
                }
            ),
        }
