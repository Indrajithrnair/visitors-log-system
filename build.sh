#!/usr/bin/env bash

# Exit on error
set -o errexit

# Print deployment information
echo "=== Starting deployment process ==="
echo "Current directory: $(pwd)"

# Install dependencies
echo "=== Installing dependencies ==="
pip install -r requirements.txt

# Collect static files
echo "=== Collecting static files ==="
python manage.py collectstatic --no-input

# Run database migrations
echo "=== Running database migrations ==="
python manage.py migrate --noinput

# Create a superuser if it doesn't exist
echo "=== Setting up admin user ==="
python << END
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'visitor_log.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError

User = get_user_model()

try:
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'Admin@123', role='ADMIN')
        print('Superuser created successfully!')
    else:
        print('Superuser already exists')
except Exception as e:
    print(f"Error working with users: {e}")
END

# Run deployment checks
echo "=== Running deployment checks ==="
python manage.py check --deploy
