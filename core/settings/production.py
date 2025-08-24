from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', default=False)

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['fernandodasilva.me'])
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


# Configuración de la base de datos
DATABASES = {
    'default': {
        'ENGINE': env('DB_ENGINE'),
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT'),
    }
}

# Configuración del servidor de correo electrónico
EMAIL_BACKEND = env(
    'EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
EMAIL_PORT = env('EMAIL_PORT')
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=False)
EMAIL_USE_SSL = env.bool('EMAIL_USE_SSL', default=True)
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')
ADMIN_EMAIL = env('ADMIN_EMAIL')

Q_CLUSTER = {
    'name': 'asiabikes',
    'timeout': 60,      # Tiempo límite por tarea (segundos)
    'retry': 120,       # Tiempo antes de reintentar (debe ser > timeout)
    'bulk': 10,
    'orm': 'default',
}
