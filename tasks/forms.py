from django import forms
from .models import Task, Project


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description", "priority", "due_date", "project"]

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields["project"].queryset = Project.objects.filter(user=user)


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Project name"}
            ),
        }
