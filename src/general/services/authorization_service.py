"""
Authorization service for access control.

This service handles authorization checks and access control logic.
It is separate from authentication and focuses on permission-based access.
"""

from typing import Callable, List, Union
from django.db.models import QuerySet
from django.contrib.auth.models import Permission
from rest_framework.response import Response

from user.models import User
from user.repositories.permission_repository import PermissionRepository


class AuthorizationService:
    """Service for authorization and access control."""
    
    def __init__(self, permission_repo: PermissionRepository = None):
        """
        Initialize AuthorizationService.
        
        Args:
            permission_repo: Permission repository instance (uses default if None)
        """
        self.permission_repo = permission_repo or PermissionRepository()
    
    def has_access(self, user_id: int, required_permission: Union[str, List[str]]) -> bool:
        """
        Check if a user has the specified permission(s).
        
        Args:
            user_id: The ID of the user to check permissions for
            required_permission: A single permission codename or list of permission codenames
            
        Returns:
            True if the user has at least one of the specified permissions, False otherwise
        """
        from user.repositories.user_repository import UserRepository
        
        user_repo = UserRepository()
        user = user_repo.get_by_id(user_id)
        user_permissions = self.permission_repo.get_user_permissions(user)
        
        if not isinstance(required_permission, list):
            required_permission = [required_permission]
        
        # Check if user has any of the required permissions
        # Using len() for backward compatibility with tests that mock QuerySets
        filtered_perms = user_permissions.filter(codename__in=required_permission)
        return len(filtered_perms) > 0
    
    def execute_with_access_check(
        self,
        endpoint: str,
        user_id: int,
        required_permission: Union[str, List[str]],
        error_message: str,
        function: Callable[[], Response]
    ) -> Response:
        """
        Execute a function if user has access, otherwise return an error response.
        
        This method combines authorization check with function execution,
        following the decorator pattern for access control.
        
        Args:
            endpoint: The API endpoint path for error logging
            user_id: The ID of the user attempting access
            required_permission: Required permission(s) - single string or list
            error_message: Error message to display if function execution fails
            function: The function to execute if user has access
            
        Returns:
            Response from the function if successful, or error response
        """
        # Import here to avoid circular dependency
        from general.security import ret_message
        
        if self.has_access(user_id, required_permission):
            try:
                return function()
            except Exception as e:
                return ret_message(
                    error_message,
                    True,
                    endpoint,
                    -1,
                    e,
                )
        else:
            return ret_message(
                "You do not have access.",
                True,
                endpoint,
                user_id,
            )
    
    def get_user_permissions(self, user_id: int) -> QuerySet[Permission]:
        """
        Get all permissions for a user based on their group memberships.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            QuerySet of Permission objects
        """
        from user.repositories.user_repository import UserRepository
        
        user_repo = UserRepository()
        user = user_repo.get_by_id(user_id)
        return self.permission_repo.get_user_permissions(user)
