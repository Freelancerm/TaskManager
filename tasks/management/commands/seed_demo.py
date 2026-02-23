"""Seed demo data for local usage."""

from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from tasks.models import Project, Task


class Command(BaseCommand):
    help = "Seed the database with demo user, projects, and tasks."

    def handle(self, *args, **options):
        username = "user"
        password = "user"
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING("Demo user already exists. Skipping."))
            return

        user = User.objects.create_user(username=username, password=password)

        work = Project.objects.create(user=user, name="Work")
        home = Project.objects.create(user=user, name="Home")
        personal = Project.objects.create(user=user, name="Personal Growth")

        today = timezone.localdate()

        Task.objects.bulk_create(
            [
                Task(
                    user=user,
                    project=None,
                    title="Inbox: capture quick ideas",
                    description="Add notes and sort later.",
                    priority=Task.PRIORITY_MEDIUM,
                    due_date=today + timedelta(days=1),
                ),
                Task(
                    user=user,
                    project=None,
                    title="Schedule dentist appointment",
                    description="Call clinic and pick a date.",
                    priority=Task.PRIORITY_HIGH,
                    due_date=today + timedelta(days=3),
                ),
                Task(
                    user=user,
                    project=work,
                    title="Finish weekly report",
                    description="Summarize KPI changes and blockers.",
                    priority=Task.PRIORITY_HIGH,
                    due_date=today + timedelta(days=2),
                ),
                Task(
                    user=user,
                    project=work,
                    title="Prepare sprint demo",
                    description="Record short walkthrough for stakeholders.",
                    priority=Task.PRIORITY_MEDIUM,
                    due_date=today + timedelta(days=5),
                ),
                Task(
                    user=user,
                    project=home,
                    title="Grocery run",
                    description="Milk, eggs, vegetables, rice.",
                    priority=Task.PRIORITY_MEDIUM,
                    due_date=today + timedelta(days=1),
                ),
                Task(
                    user=user,
                    project=home,
                    title="Clean the kitchen",
                    description="Counters, sink, and floor.",
                    priority=Task.PRIORITY_LOW,
                    due_date=today + timedelta(days=4),
                ),
                Task(
                    user=user,
                    project=personal,
                    title="Read 20 pages",
                    description="Continue the current book.",
                    priority=Task.PRIORITY_LOW,
                    due_date=today + timedelta(days=6),
                ),
                Task(
                    user=user,
                    project=personal,
                    title="Workout session",
                    description="30 min cardio + stretching.",
                    priority=Task.PRIORITY_MEDIUM,
                    due_date=today + timedelta(days=2),
                ),
            ]
        )

        self.stdout.write(self.style.SUCCESS("Demo data created. Login with user/user."))
