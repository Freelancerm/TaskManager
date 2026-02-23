#!/bin/bash

python manage.py migrate --noinput
python manage.py createsuperuser --noinput || true
python manage.py seed_demo || true
python manage.py runserver 0.0.0.0:8000
