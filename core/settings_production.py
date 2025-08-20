"""
Production settings for core project.
"""

import os
from pathlib import Path
from .settings import *

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-z&tu!p%hp3_^-%=k2tea39c#y=!2m%9+=%l9ela%e=2)*qxo-c')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Update allowed hosts for PythonAnywhere
ALLOWED_HOSTS = [
    'yourusername.pythonanywhere.com',  # Replace with your PythonAnywhere domain
    'www.yourusername.pythonanywhere.com',
    'localhost',
    '127.0.0.1',
]

# Database - Use SQLite for PythonAnywhere free tier
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Security settings for production
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# CORS settings for production
CORS_ALLOWED_ORIGINS = [
    "https://yourusername.pythonanywhere.com",
    "https://www.yourusername.pythonanywhere.com",
    "http://localhost:3000",  # If you have a frontend
    "http://127.0.0.1:3000",
]

# Disable CORS for development (remove in production)
# CORS_ALLOW_ALL_ORIGINS = True

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
