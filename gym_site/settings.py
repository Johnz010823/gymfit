"""Django settings for gym_site project."""

import os
from pathlib import Path
from dotenv import load_dotenv  # pip install python-dotenv

load_dotenv()  # Load from .env file

BASE_DIR = Path(__file__).resolve().parent.parent

# ─── Security ─────────────────────────────────────────────────────────────────
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    # Only allow fallback in local dev — never in production
    if os.environ.get('DEBUG', 'True') == 'True':
        SECRET_KEY = 'dev-only-insecure-key-change-in-production'
    else:
        raise ValueError("DJANGO_SECRET_KEY environment variable must be set in production!")

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# ─── Installed Apps ────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    # Third-party
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    # Local
    'gym_app',
    'accounts',
    'workouts',
    'attendance.apps.AttendanceConfig',
    'announcements',
    'owner',
]

# ─── Middleware ────────────────────────────────────────────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'gym_site.urls'

# ─── Templates ────────────────────────────────────────────────────────────────
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
            ],
        },
    },
]

WSGI_APPLICATION = 'gym_site.wsgi.application'

# ─── Database ─────────────────────────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ─── Password Validation ──────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ─── Localisation ─────────────────────────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Manila'
USE_I18N = True
USE_TZ = True

# ─── Static & Media ───────────────────────────────────────────────────────────
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
ACCOUNT_TEMPLATE_EXTENSION = 'html'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ─── Authentication ───────────────────────────────────────────────────────────
SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# ─── Django Allauth ───────────────────────────────────────────────────────────
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': os.environ.get('GOOGLE_CLIENT_ID', ''),
            'secret': os.environ.get('GOOGLE_CLIENT_SECRET', ''),
            'key': '',
        },
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
    }
}

# ─── Redirect URLs ────────────────────────────────────────────────────────────
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'home'

ACCOUNT_LOGIN_REDIRECT_URL = 'dashboard'
ACCOUNT_LOGOUT_REDIRECT_URL = 'home'


ACCOUNT_LOGIN_METHODS = {'username', 'email'}

ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'none'

ACCOUNT_USERNAME_MIN_LENGTH = 3

SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_LOGGING = True

# ─── Email ────────────────────────────────────────────────────────────────────
#
#  During development: emails are printed to the terminal (no SMTP needed).
#  For production:     set EMAIL_BACKEND to smtp and fill in the env vars below.
#
if DEBUG:
    # Prints the password-reset email to your terminal console instead of sending
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    # Production — requires EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in your .env
    EMAIL_BACKEND    = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST       = 'smtp.gmail.com'
    EMAIL_PORT       = 587
    EMAIL_USE_TLS    = True
    EMAIL_HOST_USER     = os.environ.get('EMAIL_HOST_USER', '')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')  # Gmail App Password
    DEFAULT_FROM_EMAIL  = EMAIL_HOST_USER

# ─── Face Encodings ───────────────────────────────────────────────────────────
FACE_ENCODINGS_DIR = BASE_DIR / 'face_data'
os.makedirs(FACE_ENCODINGS_DIR, exist_ok=True)