"""
Local settings.
Fernando Da Silva - 2025
"""

from .base import *

SECRET_KEY = env('SECRET_KEY')
DEBUG = True

ALLOWED_HOSTS = env('ALLOWED_HOSTS').split(',')

INSTALLED_APPS += [
    'django_browser_reload',
    'django_q',
]

MIDDLEWARE += [
    'django_browser_reload.middleware.BrowserReloadMiddleware',
]

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'sandbox.smtp.mailtrap.io'
EMAIL_HOST_USER = 'bbc8890f54be54'
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
EMAIL_PORT = 2525
DEFAULT_FROM_EMAIL = 'Fernando Da Silva <noreply@fernandodasilva.com>'
ADMIN_EMAIL = 'info@fernandodasilva.com'

# Django-Q Configuration
Q_CLUSTER = {
    'name': 'FDS',
    'workers': 2,
    'recycle': 500,
    'timeout': 60,
    'retry': 120,  # Must be larger than timeout
    'save_limit': 250,
    'queue_limit': 500,
    'cpu_affinity': 1,
    'label': 'Django Q',
    'redis': {
        'host': '127.0.0.1',
        'port': 6379,
        'db': 0,
    }
}

# Site URL for newsletter links
SITE_URL = 'http://localhost:8000'
