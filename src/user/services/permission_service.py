"""
Permission service for authorization business logic.

This service handles permission, group, and link management business logic.
"""

from typing import Any, Dict, List, Optional
from django.contrib.auth.models import Group, Permission
from django.db.models import Q

from user.models import Link
from user.repositories.permission_repository import PermissionRepository


class PermissionService:
    """Service for permission management business logic."""
    
    def __init__(self, permission_repo: Optional[PermissionRepository] = None):
        """
        Initialize PermissionService with dependencies.
        
        Args:
            permission_repo: Permission repository instance (uses default if None)
        """
        self.permission_repo = permission_repo or PermissionRepository()
    
    def get_all_groups(self) -> List[Group]:
        """Get all permission groups."""
        return list(self.permission_repo.get_all_groups())
    
    def save_group(self, data: Dict[str, Any]) -> Group:
        """
        Create or update a permission group and its permissions.
        
        Args:
            data: Dictionary containing group data (id, name, permissions)
            
        Returns:
            The created or updated Group object
        """
        # Create or get existing group
        if data.get("id") is None:
            group = self.permission_repo.create_group(data["name"])
        else:
            group = self.permission_repo.get_group_by_id(data["id"])
            group = self.permission_repo.update_group(group, data["name"])
        
        # Sync permissions
        if "permissions" in data:
            new_permission_ids = {p["id"] for p in data["permissions"]}
            self._sync_group_permissions(group, new_permission_ids)
        
        return group
    
    def _sync_group_permissions(self, group: Group, new_permission_ids: set) -> None:
        """
        Synchronize group's permissions.
        
        Args:
            group: Group instance
            new_permission_ids: Set of permission IDs the group should have
        """
        current_permissions = self.permission_repo.get_group_permissions(group)
        current_permission_ids = set(current_permissions.values_list('id', flat=True))
        
        # Add new permissions
        for perm_id in new_permission_ids - current_permission_ids:
            permission = self.permission_repo.get_permission_by_id(perm_id)
            self.permission_repo.add_permission_to_group(group, permission)
        
        # Remove old permissions
        for perm_id in current_permission_ids - new_permission_ids:
            permission = self.permission_repo.get_permission_by_id(perm_id)
            self.permission_repo.remove_permission_from_group(group, permission)
    
    def delete_group(self, group_id: int) -> None:
        """
        Delete a group.
        
        Args:
            group_id: The ID of the group to delete
        """
        # Import here to avoid circular dependency
        from scouting.models import ScoutAuthGroup
        
        # Clean up scout auth group if exists
        try:
            scout_auth = ScoutAuthGroup.objects.get(group__id=group_id)
            scout_auth.delete()
        except ScoutAuthGroup.DoesNotExist:
            pass
        
        group = self.permission_repo.get_group_by_id(group_id)
        self.permission_repo.delete_group(group)
    
    def get_all_permissions(self) -> List[Permission]:
        """Get all custom permissions."""
        return list(self.permission_repo.get_custom_permissions())
    
    def save_permission(self, data: Dict[str, Any]) -> Permission:
        """
        Create or update a custom permission.
        
        Args:
            data: Dictionary containing permission data (id, name, codename)
            
        Returns:
            The created or updated Permission object
        """
        if data.get("id") is None:
            return self.permission_repo.create_permission(
                name=data["name"],
                codename=data["codename"]
            )
        else:
            permission = self.permission_repo.get_permission_by_id(data["id"])
            return self.permission_repo.update_permission(
                permission,
                name=data["name"],
                codename=data["codename"]
            )
    
    def delete_permission(self, permission_id: int) -> None:
        """
        Delete a permission.
        
        Args:
            permission_id: The ID of the permission to delete
        """
        permission = self.permission_repo.get_permission_by_id(permission_id)
        self.permission_repo.delete_permission(permission)
    
    def get_all_links(self) -> List[Link]:
        """Get all navigation links."""
        return list(self.permission_repo.get_all_links())
    
    def save_link(self, data: Dict[str, Any]) -> Link:
        """
        Create or update a navigation link.
        
        Args:
            data: Dictionary containing link data (id, menu_name, routerlink, order, permission)
            
        Returns:
            The created or updated Link object
        """
        permission_id = None
        if data.get("permission") is not None:
            permission_id = data["permission"].get("id")
        
        if data.get("id") is None:
            return self.permission_repo.create_link(
                menu_name=data["menu_name"],
                routerlink=data["routerlink"],
                order=data["order"],
                permission_id=permission_id
            )
        else:
            link = self.permission_repo.get_link_by_id(data["id"])
            return self.permission_repo.update_link(
                link,
                menu_name=data["menu_name"],
                routerlink=data["routerlink"],
                order=data["order"],
                permission_id=permission_id
            )
    
    def delete_link(self, link_id: int) -> None:
        """
        Delete a navigation link.
        
        Args:
            link_id: The ID of the link to delete
        """
        link = self.permission_repo.get_link_by_id(link_id)
        self.permission_repo.delete_link(link)
