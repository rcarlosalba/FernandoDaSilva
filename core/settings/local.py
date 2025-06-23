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
