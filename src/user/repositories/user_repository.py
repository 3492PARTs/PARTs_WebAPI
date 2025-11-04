"""
User repository for data access operations.

This repository handles all database queries related to User model.
It encapsulates data access logic and provides a clean interface for services.
"""

from typing import Optional
from django.db.models import QuerySet, Q
from django.db.models.functions import Lower
from django.contrib.auth.models import Group

from user.models import User, PhoneType


class UserRepository:
    """Repository for User data access operations."""
    
    @staticmethod
    def get_by_id(user_id: int) -> User:
        """Get a user by ID."""
        return User.objects.get(id=user_id)
    
    @staticmethod
    def get_by_username(username: str) -> User:
        """Get a user by username."""
        return User.objects.get(username=username)
    
    @staticmethod
    def get_by_email(email: str) -> Optional[User]:
        """Get a user by email."""
        try:
            return User.objects.get(email=email.lower())
        except User.DoesNotExist:
            return None
    
    @staticmethod
    def filter_users(
        active: Optional[bool] = None,
        exclude_admin: bool = False
    ) -> QuerySet[User]:
        """
        Filter users by various criteria.
        
        Args:
            active: Filter by active status (None for all users)
            exclude_admin: If True, exclude users in Admin group
            
        Returns:
            QuerySet of filtered users ordered by active status and name
        """
        queryset = User.objects.all()
        
        if active is not None:
            queryset = queryset.filter(is_active=active)
        
        if exclude_admin:
            admin_group = Group.objects.filter(name="Admin").first()
            if admin_group:
                queryset = queryset.exclude(groups=admin_group)
        
        return queryset.order_by('is_active', Lower('first_name'), Lower('last_name'))
    
    @staticmethod
    def get_users_in_group(group_name: str, active_only: bool = True) -> QuerySet[User]:
        """Get all users in a specific group."""
        queryset = User.objects.filter(groups__name=group_name)
        if active_only:
            queryset = queryset.filter(is_active=True)
        return queryset
    
    @staticmethod
    def update_user(user: User, **fields) -> User:
        """
        Update user fields.
        
        Args:
            user: User instance to update
            **fields: Fields to update
            
        Returns:
            Updated user instance
        """
        for field, value in fields.items():
            if hasattr(user, field):
                setattr(user, field, value)
        user.save()
        return user
    
    @staticmethod
    def create_user(
        username: str,
        email: str,
        password: str,
        first_name: str = "",
        last_name: str = ""
    ) -> User:
        """Create a new user."""
        return User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
    
    @staticmethod
    def get_user_groups(user: User) -> QuerySet[Group]:
        """Get all groups for a user."""
        return user.groups.all().order_by('name')
    
    @staticmethod
    def add_user_to_group(user: User, group: Group) -> None:
        """Add a user to a group."""
        user.groups.add(group)
    
    @staticmethod
    def remove_user_from_group(user: User, group: Group) -> None:
        """Remove a user from a group."""
        user.groups.remove(group)
    
    @staticmethod
    def get_phone_types() -> QuerySet[PhoneType]:
        """Get all available phone types."""
        return PhoneType.objects.all().order_by('carrier')
    
    @staticmethod
    def get_phone_type_by_id(phone_type_id: int) -> PhoneType:
        """Get a phone type by ID."""
        return PhoneType.objects.get(id=phone_type_id)
    
    @staticmethod
    def delete_phone_type(phone_type: PhoneType) -> None:
        """Delete a phone type."""
        phone_type.delete()
    
    @staticmethod
    def phone_type_has_users(phone_type: PhoneType) -> bool:
        """Check if a phone type has any users associated."""
        return phone_type.user_set.exists()
