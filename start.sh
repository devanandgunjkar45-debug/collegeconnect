#!/bin/bash
set -e

echo "Starting CampusConnect application..."

# Only run migrations if DATABASE_URL is set
if [ -n "$DATABASE_URL" ]; then
    echo "Database URL found. Running migrations..."
    python manage.py migrate --noinput || echo "Migration warning: continuing startup"
else
    echo "Warning: DATABASE_URL not set. Skipping migrations."
fi

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Starting Gunicorn server..."
exec gunicorn campusconnect.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 60
