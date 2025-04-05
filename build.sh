#!/usr/bin/env bash

# Exit on error
set -o errexit

# Debug info
echo "=============== DEPLOYMENT DEBUG INFO ==============="
echo "Current working directory: $(pwd)"
echo "Python version: $(python --version)"
ls -la

# Install dependencies
echo "\n=============== INSTALLING DEPENDENCIES ==============="
pip install -r requirements.txt

# Create data directory for SQLite database
echo "\n=============== SETTING UP DATABASE ==============="
echo "Creating persistent storage directory..."
DATA_DIR="/opt/render/project/src/data"
mkdir -p "$DATA_DIR"
chmod 775 "$DATA_DIR"

# Set up static files
echo "\n=============== COLLECTING STATIC FILES ==============="
python manage.py collectstatic --no-input

# Database setup - Create fresh database if doesn't exist
SQLITE_DB="$DATA_DIR/db.sqlite3"
echo "Checking for database at $SQLITE_DB"

if [ ! -f "$SQLITE_DB" ]; then
  echo "No database found. Creating a new one..."
  touch "$SQLITE_DB"
  chmod 664 "$SQLITE_DB"
  echo "Database file created at $SQLITE_DB"
fi

# Run manual SQL to ensure database structure
echo "\n=============== PREPARING DATABASE ==============="
echo "Running migrations on $SQLITE_DB"
cd visitor_log
LS_BEFORE="$(ls -la ../data)"
echo "Database directory contents before migrations: $LS_BEFORE"

# Run migrations with verbosity for more debug info
echo "Running migrations..."
python ../manage.py migrate --noinput --verbosity 2

LS_AFTER="$(ls -la ../data)"
echo "Database directory contents after migrations: $LS_AFTER"

# Create admin user
echo "\n=============== CREATING ADMIN USER ==============="
python << END
import os
import django
import sqlite3

# Setup Django environment
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
