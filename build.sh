#!/usr/bin/env bash

# Exit on error
set -o errexit

# Modify this line as needed for your package manager (pip, poetry, etc.)
pip install -r requirements.txt

# Print current directory for debugging
echo "Current directory: $(pwd)"
ls -la

# Convert static asset files
python manage.py collectstatic --no-input

# Apply any outstanding database migrations
python manage.py migrate --noinput

# Run deployment checks
python manage.py check --deploy
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'visitor_log.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import connection

# First, verify database connection and table existence
db_path = '/opt/render/project/src/data/db.sqlite3'
print(f"Checking database at {db_path}")
print(f"Database exists: {os.path.exists(db_path)}")

# Get list of tables in the database
with connection.cursor() as cursor:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"Tables in database: {tables}")

# Try creating superuser
User = get_user_model()

try:
    # Check if we can query the user table
    try:
        users_count = User.objects.count()
        print(f"Found {users_count} users in database")
    except Exception as e:
        print(f"Error querying users: {e}")
        
    # Create superuser if it doesn't exist
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'Admin@123', role='ADMIN')
        print('Superuser created successfully!')
    else:
        print('Superuser already exists')
except Exception as e:
    print(f"Error working with users: {e}")
END

cd ..

# Run deployment checks
echo "\n=============== CHECKING DEPLOYMENT ==============="
python manage.py check --deploy
