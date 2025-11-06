"""
Compatibility shim for old 'api.asgi' module name.

This module redirects to the new 'parts_webapi.asgi' module.
"""

from parts_webapi.asgi import application  # noqa: F401

__all__ = ['application']
