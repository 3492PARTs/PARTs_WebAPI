"""
Django ORM implementation of the user repository interface.

This implementation handles all database operations for users,
keeping the business logic independent of the ORM.
"""
from typing import Optional, List
from django.db.models import QuerySet, Q
from django.db.models.functions import Lower
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import ObjectDoesNotExist

from user.models import User, PhoneType, Link
from core.interfaces.user_repository import IUserRepository


class DjangoUserRepository(IUserRepository):
    """
    Django ORM implementation of IUserRepository.
    
    This class encapsulates all database operations for users,
    providing a clean interface for the business logic layer.
    """
    
    def get_by_id(self, id: int) -> Optional[User]:
        """Retrieve a user by ID."""
        try:
            return User.objects.get(id=id)
        except User.DoesNotExist:
            return None
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Retrieve a user by username."""
        try:
            return User.objects.get(username=username.lower())
        except User.DoesNotExist:
            return None
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Retrieve a user by email address."""
        try:
            return User.objects.get(email=email.lower())
        except User.DoesNotExist:
            return None
    
    def get_all(self) -> QuerySet[User]:
        """Retrieve all users."""
        return User.objects.all().order_by('is_active', Lower('first_name'), Lower('last_name'))
    
    def filter(self, **kwargs) -> QuerySet[User]:
        """Filter users based on criteria."""
        return User.objects.filter(**kwargs)
    
    def create(self, **kwargs) -> User:
        """Create a new user."""
        return User.objects.create(**kwargs)
    
    def update(self, id: int, **kwargs) -> User:
        """Update an existing user."""
        user = self.get_by_id(id)
        if not user:
            raise ObjectDoesNotExist(f"User with id {id} not found")
        
        for key, value in kwargs.items():
            setattr(user, key, value)
        user.save()
        return user
    
    def delete(self, id: int) -> None:
        """Delete a user."""
        user = self.get_by_id(id)
        if user:
            user.delete()
    
    def exists(self, **kwargs) -> bool:
        """Check if a user exists matching the criteria."""
        return User.objects.filter(**kwargs).exists()
    
    def get_active_users(self, exclude_admin: bool = False) -> QuerySet[User]:
        """Retrieve all active users."""
        return self.get_users_by_active_status(True, exclude_admin)
    
    def get_users_by_active_status(
        self, 
        is_active: bool, 
        exclude_admin: bool = False
    ) -> QuerySet[User]:
        """
        Retrieve users filtered by active status.
        
        Args:
            is_active: Filter by active status
            exclude_admin: Whether to exclude admin users
            
        Returns:
            QuerySet of filtered users
        """
        query = Q(is_active=is_active)
        
        if exclude_admin:
            try:
                admin_group = Group.objects.get(name="Admin")
                query = query & ~Q(groups__in=[admin_group])
            except Group.DoesNotExist:
                pass  # No admin group exists yet
        
        return User.objects.filter(query).order_by(
            'is_active', 
            Lower('first_name'), 
            Lower('last_name')
        )
    
    def get_user_groups(self, user_id: int) -> QuerySet[Group]:
        """Get all groups a user belongs to."""
        user = self.get_by_id(user_id)
        if not user:
            return Group.objects.none()
        return user.groups.all().order_by('name')
    
    def get_user_permissions(self, user_id: int) -> QuerySet[Permission]:
        """
        Get all permissions for a user through their group memberships.
        
        Args:
            user_id: The user ID
            
        Returns:
            QuerySet of distinct permissions
        """
        user = self.get_by_id(user_id)
        if not user:
            return Permission.objects.none()
        
        # Get permissions from all groups the user belongs to
        user_groups = user.groups.all()
        return Permission.objects.filter(
            group__in=user_groups
        ).distinct().order_by('name')
    
    def get_users_in_group(self, group_name: str) -> QuerySet[User]:
        """Get all active users in a specific group."""
        return self.get_active_users(exclude_admin=False).filter(
            groups__name=group_name
        )
    
    def get_users_with_permission(self, permission_codename: str) -> QuerySet[User]:
        """Get all active users with a specific permission."""
        try:
            permission = Permission.objects.get(codename=permission_codename)
            groups = permission.group_set.all()
            return self.get_active_users(exclude_admin=False).filter(
                groups__in=groups
            ).distinct()
        except Permission.DoesNotExist:
            return User.objects.none()
    
    def add_user_to_groups(self, user_id: int, group_names: List[str]) -> None:
        """Add a user to multiple groups."""
        user = self.get_by_id(user_id)
        if not user:
            raise ObjectDoesNotExist(f"User with id {user_id} not found")
        
        for group_name in group_names:
            try:
                group = Group.objects.get(name=group_name)
                if not user.groups.filter(name=group_name).exists():
                    user.groups.add(group)
            except Group.DoesNotExist:
                # Log or handle missing group
                pass
    
    def remove_user_from_groups(self, user_id: int, group_names: List[str]) -> None:
        """Remove a user from multiple groups."""
        user = self.get_by_id(user_id)
        if not user:
            raise ObjectDoesNotExist(f"User with id {user_id} not found")
        
        for group_name in group_names:
            try:
                group = Group.objects.get(name=group_name)
                user.groups.remove(group)
            except Group.DoesNotExist:
                # Log or handle missing group
                pass
