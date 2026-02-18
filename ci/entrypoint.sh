#!/usr/bin/env sh
set -e

python manage.py migrate --noinput
exec gunicorn wiki.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 60
