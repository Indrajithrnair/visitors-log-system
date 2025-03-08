INSTALLED_APPS = [
    'users.apps.UsersConfig',  # Make sure this is before admin
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # ... other apps ...
] 