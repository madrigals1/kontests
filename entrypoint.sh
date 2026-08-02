#!/usr/bin/env bash
set -e

echo "Waiting for database..."
until python -c "import os,django; os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings'); django.setup(); from django.db import connection; connection.cursor()"; do
    sleep 2
done

python manage.py migrate --no-input
python manage.py scheduler &
exec python manage.py runserver 0.0.0.0:8000
