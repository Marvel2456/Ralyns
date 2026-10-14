import os
import sys
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file
load_dotenv(BASE_DIR / '.env')

# Add apps folder to python path
sys.path.insert(0, str(BASE_DIR / 'apps'))

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-ralyns-default-dev-key-2026')

DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = list(set([h.strip() for h in os.getenv('ALLOWED_HOSTS', '').split(',') if h.strip()] + ['localhost', '127.0.0.1', '0.0.0.0', 'web', 'testserver', '*']))

# Application definition
INSTALLED_APPS = [
    # Django Unfold (Must be placed before django.contrib.admin)
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.forms',
    
    # Core Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    
    # Cloudinary Storage
    'cloudinary_storage',
    'django.contrib.staticfiles',
    'cloudinary',
    
    # Ralyn's Apps
    'apps.core',
    'apps.accounts',
    'apps.logistics',
    'apps.store',
    'apps.moderation',
    'apps.owner',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.core.context_processors.brand_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'ralyns_db'),
        'USER': os.getenv('DB_USER', 'ralyns_user'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'ralyns_secure_password_2026'),
        'HOST': os.getenv('DB_HOST', 'db'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# Custom User Model
AUTH_USER_MODEL = 'accounts.CustomUser'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Lagos'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Cloudinary Media Storage Configuration
CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME', '').strip()
CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY', '').strip()
CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET', '').strip()

if CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET:
    CLOUDINARY_STORAGE = {
        'CLOUD_NAME': CLOUDINARY_CLOUD_NAME,
        'API_KEY': CLOUDINARY_API_KEY,
        'API_SECRET': CLOUDINARY_API_SECRET,
    }
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
    MEDIA_URL = f"https://res.cloudinary.com/{CLOUDINARY_CLOUD_NAME}/"
else:
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'

# Primary Key Field Type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Redis & Celery Settings
REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379/0')
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', REDIS_URL)
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', REDIS_URL)
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Resend Email Configuration
RESEND_API_KEY = os.getenv('RESEND_API_KEY', '')
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.resend.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'resend')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', RESEND_API_KEY)
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', "Ralyn's International <onboarding@resend.dev>")
SUPPORT_EMAIL = os.getenv('SUPPORT_EMAIL', 'support@ralyns.com')

LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'accounts:dashboard'
LOGOUT_REDIRECT_URL = 'core:home'

# Django Unfold Configuration
UNFOLD = {
    "SITE_TITLE": "Ralyn's International Admin",
    "SITE_HEADER": "Ralyn's International",
    "SITE_URL": "/",
    "SITE_ICON": {
        "light": lambda request: "/static/img/logo.png",
        "dark": lambda request: "/static/img/logo.png",
    },
    "SITE_SYMBOL": "local_shipping",
    "COLORS": {
        "primary": {
            "50": "254 243 199",
            "100": "253 230 138",
            "200": "252 211 77",
            "300": "245 158 11",
            "400": "217 119 6",
            "500": "216 120 8", # Brand Orange #D87808
            "600": "180 83 9",
            "700": "146 64 14",
            "800": "120 53 15",
            "900": "16 24 44", # Brand Navy #10182C
            "950": "11 15 25",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
    },
}
