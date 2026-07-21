#!/bin/bash
# Build script for Render deployment

# Exit on any error
set -e

# Collect static files
python manage.py collectstatic --noinput

# Run database migrations
python manage.py migrate
