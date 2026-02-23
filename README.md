# Task Manager

## Table of Contents
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure (key parts)](#project-structure-key-parts)
- [Run with Docker Compose](#run-with-docker-compose)
- [Local Run (without Docker)](#local-run-without-docker)
- [How to Use](#how-to-use)
- [Notes](#notes)
- [Tests](#tests)

Simple one-page task manager with projects, HTMX interactions, and user authentication.

## Features
- Create, update, delete projects.
- Create, update, delete tasks.
- Assign tasks to projects or keep them unassigned.
- Prioritize tasks (High/Medium/Low).
- Set due dates (today or future).
- Mark tasks as done with a checkbox.
- One-page UX: HTMX updates without full page reloads.
- Per-user data isolation (each user sees only their own projects and tasks).

## Tech Stack
- **Backend:** Python 3.13, Django 5.2
- **Auth:** django-allauth
- **UI:** HTML, Bootstrap 5, HTMX
- **DB:** SQLite (default)
- **Tests:** Django test framework

## Project Structure (key parts)
- `tasks/` — app with models, forms, views, URLs
- `templates/` — UI templates and HTMX partials
- `config/` — Django settings and URLs
- `docker-compose.yaml`, `Dockerfile`, `entrypoint.sh` — container setup

## Run with Docker Compose

### 1) Create `.env`
Create a `.env` file in the project root (see example.env in project):

```bash
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=admin123
```

The entrypoint runs migrations and creates a superuser using these values.
It also seeds demo data (see "Demo data" below).

### 2) Build and run
```bash
docker compose up --build
```

Open the app at:
```
http://127.0.0.1:8000/
```

## Local Run (without Docker)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## How to Use
1) Sign up or log in.
   - Demo user is preloaded: `user` / `user`.
2) Create a project in the **Projects** panel.
3) Add tasks:
   - Unassigned: use the **Tasks** panel.
   - Inside a project: expand a project and use its inline form.
4) Click the checkbox to mark a task as done.
5) Use **Edit/Delete** for quick updates.

## Notes
- Tasks are ordered by: done status, priority, nearest due date.
- Past due dates are not allowed.
- Task titles are unique per project (for a given user).

## Demo data
On container startup, the app runs `python manage.py seed_demo` to create a demo
user (`user` / `user`) with sample projects and tasks. The command is idempotent
and will skip if the user already exists.

## Tests
Run the test suite:
```bash
python manage.py test
```

## pre-commit
Install hooks locally to run linting/formatting on every commit:
```bash
pip install -r requirements.txt
pre-commit install
```

Manual run:
```bash
pre-commit run --all-files
```
