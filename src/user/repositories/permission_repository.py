"""
Permission repository for data access operations.

This repository handles all database queries related to permissions, groups, and links.
"""

from typing import List
from django.db.models import QuerySet, Q
from django.contrib.auth.models import Group, Permission

from user.models import User, Link


class PermissionRepository:
    """Repository for Permission and Group data access operations."""
    
    @staticmethod
    def get_user_permissions(user: User) -> QuerySet[Permission]:
        """
        Get all permissions for a user based on their group memberships.
        
        Args:
            user: User instance
            
        Returns:
            QuerySet of distinct Permission objects
        """
        return Permission.objects.filter(
            group__user=user
        ).distinct()
    
    @staticmethod
    def get_all_groups() -> QuerySet[Group]:
        """Get all permission groups."""
        return Group.objects.all().order_by('name')
    
    @staticmethod
    def get_group_by_id(group_id: int) -> Group:
        """Get a group by ID."""
        return Group.objects.get(id=group_id)
    
    @staticmethod
    def get_group_by_name(name: str) -> Group:
        """Get a group by name."""
        return Group.objects.get(name=name)
    
    @staticmethod
    def create_group(name: str) -> Group:
        """Create a new group."""
        group = Group(name=name)
        group.save()
        return group
    
    @staticmethod
    def update_group(group: Group, name: str) -> Group:
        """Update a group's name."""
        group.name = name
        group.save()
        return group
    
    @staticmethod
    def delete_group(group: Group) -> None:
        """Delete a group."""
        group.delete()
    
    @staticmethod
    def add_permission_to_group(group: Group, permission: Permission) -> None:
        """Add a permission to a group."""
        group.permissions.add(permission)
    
    @staticmethod
    def remove_permission_from_group(group: Group, permission: Permission) -> None:
        """Remove a permission from a group."""
        group.permissions.remove(permission)
    
    @staticmethod
    def get_group_permissions(group: Group) -> QuerySet[Permission]:
        """Get all permissions for a group."""
        return group.permissions.all()
    
    @staticmethod
    def get_custom_permissions() -> QuerySet[Permission]:
        """Get all custom permissions (content_type_id=-1)."""
        return Permission.objects.filter(content_type_id=-1).order_by('name')
    
    @staticmethod
    def get_permission_by_id(permission_id: int) -> Permission:
        """Get a permission by ID."""
        return Permission.objects.get(id=permission_id)
    
    @staticmethod
    def get_permission_by_codename(codename: str) -> Permission:
        """Get a permission by codename."""
        return Permission.objects.get(codename=codename)
    
    @staticmethod
    def create_permission(name: str, codename: str) -> Permission:
        """Create a new custom permission."""
        permission = Permission(
            name=name,
            codename=codename,
            content_type_id=-1
        )
        permission.save()
        return permission
    
    @staticmethod
    def update_permission(permission: Permission, name: str, codename: str) -> Permission:
        """Update a permission."""
        permission.name = name
        permission.codename = codename
        permission.save()
        return permission
    
    @staticmethod
    def delete_permission(permission: Permission) -> None:
        """Delete a permission."""
        permission.delete()
    
    @staticmethod
    def get_all_links() -> QuerySet[Link]:
        """Get all navigation links."""
        return Link.objects.all().order_by('order')
    
    @staticmethod
    def get_accessible_links(permissions: List[Permission]) -> QuerySet[Link]:
        """
        Get links that are accessible based on permissions.
        
        Args:
            permissions: List of Permission objects
            
        Returns:
            QuerySet of accessible Link objects
        """
        return Link.objects.filter(
            Q(permission__in=permissions) | Q(permission_id__isnull=True)
        ).order_by('order')
    
    @staticmethod
    def get_link_by_id(link_id: int) -> Link:
        """Get a link by ID."""
        return Link.objects.get(id=link_id)
    
    @staticmethod
    def create_link(menu_name: str, routerlink: str, order: int, permission_id: int = None) -> Link:
        """Create a new link."""
        link = Link(
            menu_name=menu_name,
            routerlink=routerlink,
            order=order,
            permission_id=permission_id
        )
        link.save()
        return link
    
    @staticmethod
    def update_link(link: Link, **fields) -> Link:
        """Update a link."""
        for field, value in fields.items():
            if hasattr(link, field):
                setattr(link, field, value)
        link.save()
        return link
    
    @staticmethod
    def delete_link(link: Link) -> None:
        """Delete a link."""
        link.delete()
