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
