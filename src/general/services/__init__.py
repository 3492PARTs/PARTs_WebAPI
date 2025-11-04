"""
General services module.

This module provides business logic services for cross-cutting concerns.
"""

from .authorization_service import AuthorizationService

__all__ = ['AuthorizationService']
