"""
Compatibility shim for old 'api.settings' module name.

This module redirects all imports to 'parts_webapi.settings.production'.
"""

from parts_webapi.settings.production import *  # noqa: F401, F403
