#!/bin/sh
set -e

mkdir -p /data
# python manage.py migrate --noinput
# python manage.py init_socialapps
gunicorn --bind :8000 personal_asistant.wsgi
