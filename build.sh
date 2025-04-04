#!/usr/bin/env bash

# Exit on error
set -o errexit

# Modify this line as needed for your package manager (pip, poetry, etc.)
pip install -r requirements.txt

# Print current directory for debugging
echo "Current directory: $(pwd)"
ls -la

# Print database info and settings location
echo "Database path: $(pwd)/db.sqlite3"
echo "Settings module: visitor_log.settings"

# Convert static asset files
python manage.py collectstatic --no-input

# Make sure the SQLite database directory is writable
touch db.sqlite3
chmod 666 db.sqlite3

# Force recreate database tables
echo "Running migrations from project root"
python manage.py migrate --noinput
python manage.py showmigrations

# Run deployment checks
python manage.py check --deploy
