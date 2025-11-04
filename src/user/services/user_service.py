"""
User service for business logic operations.

This service handles user management business logic, coordinating between
repositories and implementing business rules.
"""

from typing import Any, Dict, List, Optional
from django.contrib.auth.models import Group

import general.cloudinary
from user.models import User, PhoneType
from user.repositories.user_repository import UserRepository
from user.repositories.permission_repository import PermissionRepository


class UserService:
    """Service for user management business logic."""
    
    def __init__(
        self,
        user_repo: Optional[UserRepository] = None,
        permission_repo: Optional[PermissionRepository] = None
    ):
        """
        Initialize UserService with dependencies.
        
        Args:
            user_repo: User repository instance (uses default if None)
            permission_repo: Permission repository instance (uses default if None)
        """
        self.user_repo = user_repo or UserRepository()
        self.permission_repo = permission_repo or PermissionRepository()
    
    def get_user_info(self, user_id: int) -> Dict[str, Any]:
        """
        Get comprehensive user information including permissions and links.
        
        Args:
            user_id: The ID of the user to retrieve
            
        Returns:
            Dictionary containing user details, permissions, groups, and accessible links
        """
        user = self.user_repo.get_by_id(user_id)
        permissions = self.permission_repo.get_user_permissions(user)
        user_links = self.permission_repo.get_accessible_links(list(permissions))
        
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "name": user.get_full_name(),
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_active": user.is_active,
            "phone": user.phone,
            "groups": user.groups,
            "permissions": permissions,
            "phone_type": user.phone_type,
            "phone_type_id": user.phone_type_id,
            "image": general.cloudinary.build_image_url(user.img_id, user.img_ver),
            "links": user_links,
        }
    
    def get_users(
        self,
        active: Optional[int] = None,
        exclude_admin: bool = False
    ) -> List[User]:
        """
        Get a filtered list of users.
        
        Args:
            active: Filter by active status. -1 or 1 for active=True, other values for no filter
            exclude_admin: If False, exclude users in the Admin group
            
        Returns:
            List of User objects
        """
        # Convert the active parameter to boolean or None
        active_bool = None
        if active in [-1, 1]:
            active_bool = active == 1
        
        return list(self.user_repo.filter_users(
            active=active_bool,
            exclude_admin=exclude_admin
        ))
    
    def update_user(self, data: Dict[str, Any]) -> User:
        """
        Update a user's information and group memberships.
        
        Args:
            data: Dictionary containing user fields to update
            
        Returns:
            The updated User object
        """
        user = self.user_repo.get_by_username(data["username"])
        
        # Update basic user fields
        self.user_repo.update_user(
            user,
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"].lower(),
            discord_user_id=data.get("discord_user_id"),
            phone=data.get("phone"),
            phone_type_id=data.get("phone_type_id"),
            is_active=data["is_active"]
        )
        
        # Update groups if provided
        if "groups" in data:
            new_group_names = {g["name"] for g in data["groups"]}
            self._sync_user_groups(user, new_group_names)
        
        return user
    
    def _sync_user_groups(self, user: User, new_group_names: set) -> None:
        """
        Synchronize user's group memberships.
        
        Args:
            user: User instance
            new_group_names: Set of group names the user should belong to
        """
        current_groups = set(self.user_repo.get_user_groups(user).values_list('name', flat=True))
        
        # Add new groups
        for group_name in new_group_names - current_groups:
            group = self.permission_repo.get_group_by_name(group_name)
            self.user_repo.add_user_to_group(user, group)
        
        # Remove old groups
        for group_name in current_groups - new_group_names:
            group = self.permission_repo.get_group_by_name(group_name)
            self.user_repo.remove_user_from_group(user, group)
    
    def get_users_in_group(self, group_name: str) -> List[User]:
        """
        Get all active users in a specific group.
        
        Args:
            group_name: The name of the group
            
        Returns:
            List of active User objects in the specified group
        """
        return list(self.user_repo.get_users_in_group(group_name, active_only=True))
    
    def get_users_with_permission(self, permission_codename: str) -> List[User]:
        """
        Get all active users who have a specific permission through their groups.
        
        Args:
            permission_codename: The permission codename to check for
            
        Returns:
            List of distinct User objects with the specified permission
        """
        permission = self.permission_repo.get_permission_by_codename(permission_codename)
        groups = permission.group_set.all()
        group_names = [g.name for g in groups]
        
        # Get active users who are in any of these groups
        users_set = set()
        for group_name in group_names:
            users_set.update(self.user_repo.get_users_in_group(group_name, active_only=True))
        
        return list(users_set)
    
    def get_phone_types(self) -> List[PhoneType]:
        """Get all available phone types."""
        return list(self.user_repo.get_phone_types())
    
    def delete_phone_type(self, phone_type_id: int) -> None:
        """
        Delete a phone type if no users are using it.
        
        Args:
            phone_type_id: The ID of the phone type to delete
            
        Raises:
            ValueError: If there are users associated with this phone type
        """
        phone_type = self.user_repo.get_phone_type_by_id(phone_type_id)
        
        if self.user_repo.phone_type_has_users(phone_type):
            raise ValueError("Can't delete, there are users tied to this phone type.")
        
        self.user_repo.delete_phone_type(phone_type)
    
    def run_security_audit(self) -> List[User]:
        """
        Run a security audit to find active users with group memberships.
        
        Returns:
            List of active users who belong to at least one group
        """
        users = self.user_repo.filter_users(active=True, exclude_admin=False)
        return [u for u in users if u.groups.exists()]
