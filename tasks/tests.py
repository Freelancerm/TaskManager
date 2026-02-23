from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Project, Task


class TaskManagerAccessTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="u1", password="pass")
        self.other_user = User.objects.create_user(username="u2", password="pass")
        self.project = Project.objects.create(user=self.user, name="P1")
        self.other_project = Project.objects.create(user=self.other_user, name="P2")
        self.task = Task.objects.create(
            user=self.user,
            project=self.project,
            title="T1",
            due_date=date.today(),
        )

    def test_home_requires_login(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("account_login"), response["Location"])

    def test_project_update_denied_for_other_user(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("project-update", args=[self.other_project.id])
        )
        self.assertEqual(response.status_code, 404)

    def test_task_update_denied_for_other_user(self):
        other_task = Task.objects.create(
            user=self.other_user, project=self.other_project, title="OT"
        )
        self.client.force_login(self.user)
        response = self.client.get(reverse("task-update", args=[other_task.id]))
        self.assertEqual(response.status_code, 404)


class TaskManagerHTMXTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="u1", password="pass")
        self.project = Project.objects.create(user=self.user, name="P1")
        self.client.force_login(self.user)

    def test_create_project_htmx(self):
        response = self.client.post(
            reverse("project-create"),
            {"name": "New Project"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "New Project")
        self.assertTrue(Project.objects.filter(user=self.user, name="New Project").exists())

    def test_update_project_htmx(self):
        response = self.client.post(
            reverse("project-update", args=[self.project.id]),
            {"name": "Renamed"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.project.refresh_from_db()
        self.assertEqual(self.project.name, "Renamed")

    def test_delete_project_htmx(self):
        response = self.client.delete(
            reverse("project-delete", args=[self.project.id]),
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Project.objects.filter(id=self.project.id).exists())

    def test_create_task_htmx_unassigned(self):
        response = self.client.post(
            reverse("task-create"),
            {
                "title": "Task 1",
                "description": "Desc",
                "priority": Task.PRIORITY_MEDIUM,
                "due_date": date.today().isoformat(),
                "project": "",
            },
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Task 1")
        self.assertTrue(Task.objects.filter(user=self.user, title="Task 1").exists())

    def test_update_task_htmx(self):
        task = Task.objects.create(user=self.user, title="Old", project=None)
        response = self.client.post(
            reverse("task-update", args=[task.id]),
            {
                "title": "New",
                "description": "",
                "priority": Task.PRIORITY_HIGH,
                "due_date": "",
                "project": "",
            },
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        task.refresh_from_db()
        self.assertEqual(task.title, "New")
        self.assertEqual(task.priority, Task.PRIORITY_HIGH)

    def test_toggle_task_htmx(self):
        task = Task.objects.create(user=self.user, title="Toggle", project=None)
        response = self.client.post(
            reverse("task-toggle", args=[task.id]),
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        task.refresh_from_db()
        self.assertTrue(task.is_done)

    def test_delete_task_htmx(self):
        task = Task.objects.create(user=self.user, title="Delete", project=None)
        response = self.client.delete(
            reverse("task-delete", args=[task.id]),
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Task.objects.filter(id=task.id).exists())
