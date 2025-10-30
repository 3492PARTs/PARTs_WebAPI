"""
Test settings for PARTs WebAPI.
Minimal Django settings for testing without requiring .env files or JWT keys.
"""
import os
from pathlib import Path
from datetime import timedelta

# Set required environment variables
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-only-12345")
os.environ.setdefault("DEBUG", "True")
os.environ.setdefault("FRONTEND_ADDRESS", "http://localhost:3000")
os.environ.setdefault("ENVIRONMENT", "test")

# Build paths - BASE_DIR points to repository root
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

# Basic Django settings
SECRET_KEY = "test-secret-key-for-testing-only-12345"
DEBUG = True
ENVIRONMENT = "test"
VERSION = "BUILD"
FRONTEND_ADDRESS = "http://localhost:3000"

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    "admin.apps.AdminConfig",
    "alerts.apps.AlertsConfig",
    "form.apps.FormConfig",
    "public.apps.PublicConfig",
    "scouting.apps.ScoutingConfig",
    "sponsoring.apps.SponsoringConfig",
    "tba.apps.TbaConfig",
    "user.apps.UserConfig",
    "attendance.apps.AttendanceConfig",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "corsheaders",
    "rest_framework",
    "simple_history",
    "webpush",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
]

CORS_ORIGIN_WHITELIST = [
    "http://localhost:3000",
]

CORS_ALLOW_CREDENTIALS = True

ROOT_URLCONF = "parts_webapi.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
            ],
        },
    },
]

WSGI_APPLICATION = "parts_webapi.wsgi.application"

# Database - use in-memory SQLite for tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable migrations for faster tests
class DisableMigrations:
    def __contains__(self, item):
        return True
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Password validation
AUTH_PASSWORD_VALIDATORS = []

# Simplified password hashing for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "America/New_York"
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# REST Framework configuration
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
}

# Simple JWT - use HS256 for testing (doesn't require key files)
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=3),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",  # Use symmetric algorithm for testing
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    "AUDIENCE": None,
    "ISSUER": None,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "JTI_CLAIM": "jti",
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),
}

AUTH_USER_MODEL = "user.User"
AUTHENTICATION_BACKENDS = ["user.views.UserLogIn"]

# Email backend for tests
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
DEFAULT_FROM_EMAIL = "test@example.com"

# Cloudinary settings (mocked in tests)
CLOUDINARY_URL = "cloudinary://test:test@test"

# WebPush settings
WEBPUSH_SETTINGS = {
    "VAPID_PUBLIC_KEY": "test-public-key",
    "VAPID_PRIVATE_KEY": "test-private-key",
    "VAPID_ADMIN_EMAIL": "test@example.com"
}

# TBA settings
TBA_KEY = "test-tba-key"
TBA_WEBHOOK_SECRET = "test-webhook-secret"
DISCORD_NOTIFICATION_WEBHOOK = ""

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}
