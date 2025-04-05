#!/usr/bin/env bash

# Exit on error
set -o errexit

# Modify this line as needed for your package manager (pip, poetry, etc.)
pip install -r requirements.txt

# Print current directory for debugging
echo "Current directory: $(pwd)"
ls -la

# Ensure the persistent disk directory exists
echo "Setting up persistent storage for SQLite..."
if [ ! -d "/opt/render/project/src/data" ]; then
  echo "Creating data directory..."
  mkdir -p "/opt/render/project/src/data"
fi

# If there's an existing database in the project directory, copy it to the persistent disk
if [ -f "db.sqlite3" ] && [ ! -f "/opt/render/project/src/data/db.sqlite3" ]; then
  echo "Copying existing SQLite database to persistent storage..."
  cp "db.sqlite3" "/opt/render/project/src/data/db.sqlite3"
  chmod 664 "/opt/render/project/src/data/db.sqlite3"
fi

# Convert static asset files
python manage.py collectstatic --no-input

# Apply any outstanding database migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Create a superuser if it doesn't exist (use environment variables for credentials)
echo "Setting up admin user..."
python << END
import os
import django
dj_settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', 'visitor_log.settings')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', dj_settings_module)
django.setup()

from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError

User = get_user_model()

try:
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'Admin@123', role='ADMIN')
        print('Superuser created successfully!')
    else:
        print('Superuser already exists.')
except IntegrityError as e:
    print(f'Error creating superuser: {e}')
END

# Run deployment checks
python manage.py check --deploy
