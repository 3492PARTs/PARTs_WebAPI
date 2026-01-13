from typing import Any
from django.contrib.auth.models import Group, Permission
from django.db.models import Q, QuerySet
from django.db.models.functions import Lower

from scouting.models import ScoutAuthGroup
from user.models import User, PhoneType, Link
import general.cloudinary
import general.security


def get_user(user_id: int) -> User:
    """
    Get user object.

    Args:
        user_id: The ID of the user to retrieve

    Returns:
        User object
    """
    return User.objects.get(id=user_id)


def get_user_parsed(user_id: int) -> dict[str, Any]:
    """
    Get comprehensive user information including permissions and links.

    Args:
        user_id: The ID of the user to retrieve

    Returns:
        Dictionary containing user details, permissions, groups, and accessible links
    """
    usr = get_user(user_id)

    return parse_user(usr)


def parse_user(usr: User) -> dict[str, Any]:
    """
    Parse a User object into a dictionary with detailed information.

    Args:
        usr: The User object to parse

    Returns:
        Dictionary containing user details, permissions, groups, and accessible links
    """
    permissions = general.security.get_user_permissions(usr.id)

    user_links = Link.objects.filter(
        Q(permission__in=permissions) | Q(permission_id__isnull=True)
    ).order_by("order")

    usr_dict = {
        "id": usr.id,
        "username": usr.username,
        "email": usr.email,
        "name": usr.get_full_name(),
        "first_name": usr.first_name,
        "last_name": usr.last_name,
        "is_active": usr.is_active,
        "phone": usr.phone,
        "groups": usr.groups,
        "permissions": permissions,
        "phone_type": usr.phone_type,
        "phone_type_id": usr.phone_type_id,
        "image": general.cloudinary.build_image_url(usr.img_id, usr.img_ver),
        "links": user_links,
    }

    return usr_dict


def get_users(active: int, admin: bool) -> QuerySet[User]:
    """
    Get a filtered list of users based on active status and admin exclusion.

    Args:
        active: Filter by active status. -1 or 1 for active=True, other values for no filter
        admin: If False, exclude users in the Admin group

    Returns:
        QuerySet of User objects ordered by active status and name
    """
    user_active = Q()
    if active in [-1, 1]:
        user_active = Q(is_active=active == 1)

    user_admin = Q()
    if not admin:
        group = Group.objects.get(name="Admin")
        user_admin = Q(groups__in=[group])

    users = (
        User.objects.filter(user_active)
        .exclude(user_admin)
        .order_by("is_active", Lower("first_name"), Lower("last_name"))
    )

    # Q(date_joined__isnull=False) &

    return users


def get_users_parsed(active: int, admin: bool) -> list[dict[str, Any]]:
    """
    Get a list of parsed user dictionaries based on active status and admin exclusion.

    Args:
        active: Filter by active status. -1 or 1 for active=True, other values for no filter
        admin: If False, exclude users in the Admin group
    Returns:
        List of dictionaries containing user details
    """
    users = get_users(active, admin)
    users_parsed = []

    for u in users:
        users_parsed.append(parse_user(u))

    return users_parsed


def save_user(data: dict[str, Any]) -> User:
    """
    Update a user's information and group memberships.

    Args:
        data: Dictionary containing user fields to update (username, first_name, last_name,
              email, discord_user_id, phone, phone_type_id, is_active, groups)

    Returns:
        The updated User object
    """
    groups = []
    u = User.objects.get(username=data["username"])
    u.first_name = data["first_name"]
    u.last_name = data["last_name"]
    u.email = data["email"].lower()
    u.discord_user_id = data["discord_user_id"]
    u.phone = data["phone"]
    u.phone_type_id = data.get("phone_type_id", None)
    u.is_active = data["is_active"]
    u.save()

    if "groups" in data:
        for d in data["groups"]:
            groups.append(d["name"])
            aug = u.groups.filter(name=d["name"]).exists()
            if not aug:
                group = Group.objects.get(name=d["name"])
                u.groups.add(group)

        user_groups = u.groups.filter(~Q(name__in=groups))

        for user_group in user_groups:
            user_group.user_set.remove(u)

    return u


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

    Returns:
        QuerySet of PhoneType objects ordered by carrier
    """
    return PhoneType.objects.all().order_by("carrier")


def delete_phone_type(phone_type_id: int) -> None:
    """
    Delete a phone type if no users are using it.

    Args:
        phone_type_id: The ID of the phone type to delete

    Raises:
        ValueError: If there are users associated with this phone type
    """
    phone_type = PhoneType.objects.get(id=phone_type_id)

    if phone_type.user_set.exists():
        raise ValueError("Can't delete, there are users tied to this phone type.")

    phone_type.delete()


def get_users_in_group(name: str) -> QuerySet[User]:
    """
    Get all active users in a specific group.

    Args:
        name: The name of the group

    Returns:
        QuerySet of active User objects in the specified group
    """
    return get_users(1, 1).filter(groups__name=name)


def get_users_with_permission(codename: str) -> QuerySet[User]:
    """
    Get all active users who have a specific permission through their group memberships.

    Args:
        codename: The permission codename to check for

    Returns:
        QuerySet of distinct User objects with the specified permission
    """
    users = []
    prmsn = Permission.objects.get(codename=codename)
    groups = set(g.name for g in prmsn.group_set.all())
    users = get_users(1, 1).filter(groups__name__in=groups).distinct()

    return users


def get_groups() -> QuerySet[Group]:
    """
    Get all available permission groups.

    Returns:
        QuerySet of Group objects ordered by name
    """
    return Group.objects.all().order_by("name")


def save_group(data: dict[str, Any]) -> None:
    """
    Create or update a permission group and its permissions.

    Args:
        data: Dictionary containing group data (id, name, permissions)
              If id is None, creates a new group
    """
    if data.get("id", None) is None:
        group = Group(name=data.get("name"))
    else:
        group = Group.objects.get(id=data["id"])
        group.name = data.get("name")

    group.save()

    prmsn_ids = []
    for prm in data.get("permissions", []):
        prmsn_ids.append(prm["id"])
        gpr_prmsn = group.permissions.filter(id=prm["id"]).exists()
        if not gpr_prmsn:
            permission = Permission.objects.get(id=prm["id"])
            group.permissions.add(permission)

    gpr_prmsns = group.permissions.filter(~Q(id__in=prmsn_ids))

    for gpr_prmsn in gpr_prmsns:
        gpr_prmsn.group_set.remove(group)


def delete_group(group_id: int) -> None:
    """
    Delete a group and its scout auth group association if it exists.

    Args:
        group_id: The ID of the group to delete
    """
    try:
        ScoutAuthGroup.objects.get(group__id=group_id).delete()
    except ScoutAuthGroup.DoesNotExist:
        pass
    Group.objects.get(id=group_id).delete()


def get_permissions() -> QuerySet[Permission]:
    """
    Get all custom permissions (those with content_type_id=-1).

    Returns:
        QuerySet of Permission objects ordered by name
    """
    return Permission.objects.filter(content_type_id=-1).order_by("name")


def save_permission(data: dict[str, Any]) -> None:
    """
    Create or update a custom permission.

    Args:
        data: Dictionary containing permission data (id, name, codename)
              If id is None, creates a new permission
    """
    if data.get("id", None) is None:
        prmsn = Permission(name=data["name"])
    else:
        prmsn = Permission.objects.get(id=data["id"])
        prmsn.name = data["name"]

    prmsn.codename = data["codename"]
    prmsn.content_type_id = -1

    prmsn.save()


def delete_permission(prmsn_id: int):
    Permission.objects.get(id=prmsn_id).delete()


def run_security_audit():
    users = get_users(1, 1)

    users_ret = []

    for u in users:
        if len(u.groups.all()) > 0:
            users_ret.append(u)

    return users_ret


def get_links():
    return Link.objects.all().order_by("order")


def save_link(data):
    if data.get("id", None) is None:
        link = Link()
    else:
        link = Link.objects.get(id=data["id"])

    link.menu_name = data["menu_name"]
    link.permission_id = (
        None
        if data.get("permission", None) is None
        else data.get("permission", None).get("id", None)
    )
    link.routerlink = data["routerlink"]
    link.order = data["order"]

    link.save()


def delete_link(link_id: int):
    Link.objects.get(id=link_id).delete()
