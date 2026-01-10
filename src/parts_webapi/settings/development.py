"""
Development settings for PARTs WebAPI project.
"""

from .base import *

# Enable debug mode in development
DEBUG = True

# ALLOWED_HOSTS for development
ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
]

# CORS settings for development
CORS_ORIGIN_WHITELIST = [
    "http://127.0.0.1",
    "http://localhost:4200",
    "http://localhost:3000",
]

# Use console email backend for development
# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
