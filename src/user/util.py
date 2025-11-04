from typing import Any
from django.contrib.auth.models import Group, Permission
from django.db.models import Q, QuerySet
from django.db.models.functions import Lower

from scouting.models import ScoutAuthGroup
from user.models import User, PhoneType, Link
import general.cloudinary
import general.security

# Import new service layer
from user.services.user_service import UserService
from user.services.permission_service import PermissionService


def get_user(user_id: int) -> dict[str, Any]:
    """
    Get comprehensive user information including permissions and links.
    
    DEPRECATED: Use UserService.get_user_info() instead.
    This function is maintained for backward compatibility.
    
    Args:
        user_id: The ID of the user to retrieve
        
    Returns:
        Dictionary containing user details, permissions, groups, and accessible links
    """
    service = UserService()
    return service.get_user_info(user_id)


def get_users(active: int, admin: bool) -> QuerySet[User]:
    """
    Get a filtered list of users based on active status and admin exclusion.
    
    DEPRECATED: Use UserService.get_users() instead.
    This function is maintained for backward compatibility.
    
    Args:
        active: Filter by active status. -1 or 1 for active=True, other values for no filter
        admin: If False, exclude users in the Admin group
        
    Returns:
        QuerySet of User objects ordered by active status and name
    """
    service = UserService()
    users_list = service.get_users(active=active, exclude_admin=not admin)
    # Return as QuerySet for compatibility - convert list back to queryset IDs
    if users_list:
        user_ids = [u.id for u in users_list]
        return User.objects.filter(id__in=user_ids).order_by('is_active', Lower('first_name'), Lower('last_name'))
    return User.objects.none()


def save_user(data: dict[str, Any]) -> User:
    """
    Update a user's information and group memberships.
    
    DEPRECATED: Use UserService.update_user() instead.
    This function is maintained for backward compatibility.
    
    Args:
        data: Dictionary containing user fields to update
        
    Returns:
        The updated User object
    """
    service = UserService()
    return service.update_user(data)


def get_user_groups(user_id: int) -> QuerySet[Group]:
    """
    Get all groups a user belongs to.
    
    Args:
        user_id: The ID of the user
        
    Returns:
        QuerySet of Group objects ordered by name
    """
    user_groups = User.objects.get(id=user_id).groups.all().order_by("name")

    return user_groups


def get_phone_types() -> QuerySet[PhoneType]:
    """
    Get all available phone types for SMS messaging.
    
    DEPRECATED: Use UserService.get_phone_types() instead.
    This function is maintained for backward compatibility.
    
    Returns:
        QuerySet of PhoneType objects ordered by carrier
    """
    service = UserService()
    types_list = service.get_phone_types()
    if types_list:
        type_ids = [t.id for t in types_list]
        return PhoneType.objects.filter(id__in=type_ids).order_by('carrier')
    return PhoneType.objects.none()


def delete_phone_type(phone_type_id: int) -> None:
    """
    Delete a phone type if no users are using it.
    
    DEPRECATED: Use UserService.delete_phone_type() instead.
    This function is maintained for backward compatibility.
    
    Args:
        phone_type_id: The ID of the phone type to delete
        
    Raises:
        ValueError: If there are users associated with this phone type
    """
    service = UserService()
    service.delete_phone_type(phone_type_id)


def get_users_in_group(name: str) -> QuerySet[User]:
    """
    Get all active users in a specific group.
    
    DEPRECATED: Use UserService.get_users_in_group() instead.
    This function is maintained for backward compatibility.
    
    Args:
        name: The name of the group
        
    Returns:
        QuerySet of active User objects in the specified group
    """
    service = UserService()
    users_list = service.get_users_in_group(name)
    if users_list:
        user_ids = [u.id for u in users_list]
        return User.objects.filter(id__in=user_ids)
    return User.objects.none()


def get_users_with_permission(codename: str) -> QuerySet[User]:
    """
    Get all active users who have a specific permission through their group memberships.
    
    DEPRECATED: Use UserService.get_users_with_permission() instead.
    This function is maintained for backward compatibility.
    
    Args:
        codename: The permission codename to check for
        
    Returns:
        QuerySet of distinct User objects with the specified permission
    """
    service = UserService()
    users_list = service.get_users_with_permission(codename)
    if users_list:
        user_ids = [u.id for u in users_list]
        return User.objects.filter(id__in=user_ids).distinct()
    return User.objects.none()


def get_groups() -> QuerySet[Group]:
    """
    Get all available permission groups.
    
    DEPRECATED: Use PermissionService.get_all_groups() instead.
    This function is maintained for backward compatibility.
    
    Returns:
        QuerySet of Group objects ordered by name
    """
    service = PermissionService()
    groups_list = service.get_all_groups()
    if groups_list:
        group_ids = [g.id for g in groups_list]
        return Group.objects.filter(id__in=group_ids).order_by('name')
    return Group.objects.none()


def save_group(data: dict[str, Any]) -> None:
    """
    Create or update a permission group and its permissions.
    
    DEPRECATED: Use PermissionService.save_group() instead.
    This function is maintained for backward compatibility.
    
    Args:
        data: Dictionary containing group data (id, name, permissions)
    """
    service = PermissionService()
    service.save_group(data)


def delete_group(group_id: int) -> None:
    """
    Delete a group and its scout auth group association if it exists.
    
    DEPRECATED: Use PermissionService.delete_group() instead.
    This function is maintained for backward compatibility.
    
    Args:
        group_id: The ID of the group to delete
    """
    service = PermissionService()
    service.delete_group(group_id)


def get_permissions() -> QuerySet[Permission]:
    """
    Get all custom permissions (those with content_type_id=-1).
    
    DEPRECATED: Use PermissionService.get_all_permissions() instead.
    This function is maintained for backward compatibility.
    
    Returns:
        QuerySet of Permission objects ordered by name
    """
    service = PermissionService()
    perms_list = service.get_all_permissions()
    if perms_list:
        perm_ids = [p.id for p in perms_list]
        return Permission.objects.filter(id__in=perm_ids).order_by('name')
    return Permission.objects.none()


def save_permission(data: dict[str, Any]) -> None:
    """
    Create or update a custom permission.
    
    DEPRECATED: Use PermissionService.save_permission() instead.
    This function is maintained for backward compatibility.
    
    Args:
        data: Dictionary containing permission data (id, name, codename)
    """
    service = PermissionService()
    service.save_permission(data)


def delete_permission(prmsn_id: int):
    """
    Delete a permission.
    
    DEPRECATED: Use PermissionService.delete_permission() instead.
    This function is maintained for backward compatibility.
    
    Args:
        prmsn_id: The ID of the permission to delete
    """
    service = PermissionService()
    service.delete_permission(prmsn_id)


def run_security_audit():
    """
    Run security audit.
    
    DEPRECATED: Use UserService.run_security_audit() instead.
    This function is maintained for backward compatibility.
    
    Returns:
        List of users with group memberships
    """
    service = UserService()
    return service.run_security_audit()


def get_links():
    """
    Get all navigation links.
    
    DEPRECATED: Use PermissionService.get_all_links() instead.
    This function is maintained for backward compatibility.
    
    Returns:
        QuerySet of Link objects
    """
    service = PermissionService()
    links_list = service.get_all_links()
    if links_list:
        link_ids = [link.id for link in links_list]
        return Link.objects.filter(id__in=link_ids).order_by('order')
    return Link.objects.none()


def save_link(data):
    """
    Create or update a navigation link.
    
    DEPRECATED: Use PermissionService.save_link() instead.
    This function is maintained for backward compatibility.
    
    Args:
        data: Dictionary containing link data
    """
    service = PermissionService()
    service.save_link(data)


def delete_link(link_id: int):
    """
    Delete a navigation link.
    
    DEPRECATED: Use PermissionService.delete_link() instead.
    This function is maintained for backward compatibility.
    
    Args:
        link_id: The ID of the link to delete
    """
    service = PermissionService()
    service.delete_link(link_id)
