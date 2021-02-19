#!/bin/bash
python manage.py collectstatic --noinput&&
python manage.py makemigrations&&
python manage.py migrate&&
python manage.py rebuild_index --noinput
gunicorn myblog.wsgi:application -c gunicorn.conf