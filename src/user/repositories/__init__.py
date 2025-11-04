"""
User data access repositories.

This module contains data access logic for user-related operations.
Repositories handle all database queries and updates.
"""

from .user_repository import UserRepository
from .permission_repository import PermissionRepository

__all__ = ['UserRepository', 'PermissionRepository']
