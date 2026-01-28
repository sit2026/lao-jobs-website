"""
Django settings for production (Railway).
"""
import os
import dj_database_url
from .base import *

DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'

# Use English since Lao translations not available
LANGUAGE_CODE = 'en-us'

# Generate a default secret key if not provided (not ideal but works for demo)
import secrets
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', secrets.token_urlsafe(50))

# Allow Railway domain and custom domains
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '.pythonanywhere.com,.railway.app,.onrender.com,localhost').split(',')

# Railway provides CSRF trusted origins
CSRF_TRUSTED_ORIGINS = [
    'https://*.pythonanywhere.com',
    'https://*.railway.app',
    'https://*.up.railway.app',
    'https://*.onrender.com',
]
if os.environ.get('SITE_URL'):
    CSRF_TRUSTED_ORIGINS.append(os.environ.get('SITE_URL'))

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Only enable SSL redirect if not in Railway (they handle SSL)
SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'false').lower() == 'true'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Database - Railway provides DATABASE_URL
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Cache - use local memory if no Redis
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Use database sessions instead of cache sessions
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Whitenoise for static files
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Static files
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# CORS
CORS_ALLOW_ALL_ORIGINS = True
