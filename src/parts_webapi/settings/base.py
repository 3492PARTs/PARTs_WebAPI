"""
Django base settings for PARTs WebAPI project.

This file contains settings common to all environments.
Environment-specific settings are in development.py and production.py.
"""

from datetime import timedelta
import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# BASE_DIR points to the repository root (parent of src/)
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

# Load environment variables from .env file if it exists
env_file = BASE_DIR / ".env"
if env_file.exists():
    load_dotenv(env_file)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv(
    "SECRET_KEY", "django-insecure-dev-key-change-in-production-12345678901234567890"
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
DEBUG_PROPAGATE_EXCEPTIONS = DEBUG

FRONTEND_ADDRESS = os.getenv("FRONTEND_ADDRESS", "http://localhost:3000")
ENVIRONMENT = os.getenv("ENVIRONMENT", "local")
VERSION = "BUILD"

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

ROOT_URLCONF = "api.urls"

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
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "api.wsgi.application"

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases
db_engine = os.getenv("DB_ENGINE", "django.db.backends.sqlite3")

DATABASES = {
    "default": {
        "ENGINE": db_engine,
        "NAME": (
            os.getenv("DB_NAME", "")
            if db_engine != "django.db.backends.sqlite3"
            else str(BASE_DIR / "db.sqlite3")
        ),
        "USER": os.getenv("DB_USER", ""),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", ""),
        "PORT": os.getenv("DB_PORT", ""),
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=3),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
}

# Try to load RSA keys if they exist, otherwise use HS256 for development
jwt_key_path = BASE_DIR / "keys/jwt-key"
jwt_pub_key_path = BASE_DIR / "keys/jwt-key.pub"

if jwt_key_path.exists() and jwt_pub_key_path.exists():
    SIMPLE_JWT.update(
        {
            "ALGORITHM": "RS512",
            "SIGNING_KEY": open(jwt_key_path).read(),
            "VERIFYING_KEY": open(jwt_pub_key_path).read(),
        }
    )
else:
    # Fallback to symmetric key for development
    SIMPLE_JWT.update(
        {
            "ALGORITHM": "HS256",
            "SIGNING_KEY": SECRET_KEY,
            "VERIFYING_KEY": None,
        }
    )

SIMPLE_JWT.update(
    {
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
)

AUTH_USER_MODEL = "user.User"

AUTHENTICATION_BACKENDS = ["user.views.UserLogIn"]

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/
# STATIC_ROOT = BASE_DIR / 'staticfiles'
# STATIC_URL = '/static/'
# STATICFILES_DIRS = [BASE_DIR / 'static']

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Email and SMTP settings
DEFAULT_FROM_EMAIL = os.getenv("EMAIL_FROM", "noreply@parts3492.org")
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_USE_TLS = True
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_PORT = os.getenv("EMAIL_PORT", "587")

# Cloudinary
os.environ["CLOUDINARY_URL"] = os.getenv("CLOUDINARY_URL", "")

# The Blue Alliance API
TBA_KEY = os.getenv("TBA_KEY", "")
TBA_WEBHOOK_SECRET = os.getenv("TBA_WEBHOOK_SECRET", "")

# Discord integration
DISCORD_NOTIFICATION_WEBHOOK = os.getenv("DISCORD_NOTIFICATION_WEBHOOK", "")

# WebPush settings
WEBPUSH_SETTINGS = {
    "VAPID_PUBLIC_KEY": os.getenv("VAPID_PUBLIC_KEY", ""),
    "VAPID_PRIVATE_KEY": os.getenv("VAPID_PRIVATE_KEY", ""),
    "VAPID_ADMIN_EMAIL": os.getenv("VAPID_ADMIN_EMAIL", ""),
}
