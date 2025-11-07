"""
User repository interface defining contracts for user data access.

This interface extends the base repository with user-specific operations.
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from django.db.models import QuerySet
from django.contrib.auth.models import Group, Permission

from core.interfaces.repository import IRepository


class IUserRepository(IRepository):
    """
    Interface for user data access operations.
    
    Extends the base repository with user-specific queries
    and operations for authentication and authorization.
    """
    
    @abstractmethod
    def get_by_username(self, username: str) -> Optional[Any]:
        """
        Retrieve a user by username.
        
        Args:
            username: The username to search for
            
        Returns:
            User if found, None otherwise
        """
        pass
    
    @abstractmethod
    def get_by_email(self, email: str) -> Optional[Any]:
        """
        Retrieve a user by email address.
        
        Args:
            email: The email to search for
            
        Returns:
            User if found, None otherwise
        """
        pass
    
    @abstractmethod
    def get_active_users(self, exclude_admin: bool = False) -> QuerySet:
        """
        Retrieve all active users.
        
        Args:
            exclude_admin: Whether to exclude admin users
            
        Returns:
            QuerySet of active users
        """
        pass
    
    @abstractmethod
    def get_users_by_active_status(self, is_active: bool, exclude_admin: bool = False) -> QuerySet:
        """
        Retrieve users filtered by active status.
        
        Args:
            is_active: Filter by active status
            exclude_admin: Whether to exclude admin users
            
        Returns:
            QuerySet of filtered users
        """
        pass
    
    @abstractmethod
    def get_user_groups(self, user_id: int) -> QuerySet[Group]:
        """
        Get all groups a user belongs to.
        
        Args:
            user_id: The user ID
            
        Returns:
            QuerySet of groups
        """
        pass
    
    @abstractmethod
    def get_user_permissions(self, user_id: int) -> QuerySet[Permission]:
        """
        Get all permissions for a user.
        
        Args:
            user_id: The user ID
            
        Returns:
            QuerySet of permissions
        """
        pass
    
    @abstractmethod
    def get_users_in_group(self, group_name: str) -> QuerySet:
        """
        Get all users in a specific group.
        
        Args:
            group_name: Name of the group
            
        Returns:
            QuerySet of users
        """
        pass
    
    @abstractmethod
    def get_users_with_permission(self, permission_codename: str) -> QuerySet:
        """
        Get all users with a specific permission.
        
        Args:
            permission_codename: The permission codename
            
        Returns:
            QuerySet of users
        """
        pass
    
    @abstractmethod
    def add_user_to_groups(self, user_id: int, group_names: List[str]) -> None:
        """
        Add a user to multiple groups.
        
        Args:
            user_id: The user ID
            group_names: List of group names
        """
        pass
    
    @abstractmethod
    def remove_user_from_groups(self, user_id: int, group_names: List[str]) -> None:
        """
        Remove a user from multiple groups.
        
        Args:
            user_id: The user ID
            group_names: List of group names
        """
        pass
