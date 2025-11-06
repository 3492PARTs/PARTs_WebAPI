"""
Compatibility shim for old 'api.wsgi' module name.

This module redirects to the new 'parts_webapi.wsgi' module.
"""

from parts_webapi.wsgi import application  # noqa: F401

__all__ = ['application']
