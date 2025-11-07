"""
Production settings for PARTs WebAPI project.
"""

from .base import *

# DEBUG should always be False in production
DEBUG = False
DEBUG_PROPAGATE_EXCEPTIONS = False

# ALLOWED_HOSTS based on ENVIRONMENT
ALLOWED_HOSTS = []

if ENVIRONMENT == "main":
    ALLOWED_HOSTS = [
        "parts3492.org",
        "api.parts3492.org",
    ]
elif ENVIRONMENT == "uat":
    ALLOWED_HOSTS = [
        "partsuat.bduke.dev",
    ]
else:
    # Default production hosts
    ALLOWED_HOSTS = [
        "parts3492.bduke.dev",
        "partsuat.bduke.dev",
    ]

# CORS settings for production
CORS_ORIGIN_WHITELIST = []

if ENVIRONMENT == "main":
    CORS_ORIGIN_WHITELIST = [
        "https://parts3492.org",
        "https://www.parts3492.org",
    ]
else:
    CORS_ORIGIN_WHITELIST = [
        "https://parts3492.bduke.dev",
        "https://www.parts3492.bduke.dev",
    ]

# Security settings for production
# SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "True").lower() in ("true", "1", "t")
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
# SECURE_BROWSER_XSS_FILTER = True
# SECURE_CONTENT_TYPE_NOSNIFF = True
# X_FRAME_OPTIONS = "DENY"
