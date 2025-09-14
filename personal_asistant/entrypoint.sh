#!/bin/sh
set -e

#mkdir -p /data
#python manage.py migrate --noinput
python manage.py init_socialapps
exec daphne -b 0.0.0.0 -p ${PORT:-8000} personal_asistant.asgi:application