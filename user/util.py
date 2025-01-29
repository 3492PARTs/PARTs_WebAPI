from django.contrib.auth.models import Group, Permission
from django.db.models import Q, Value, Count
from django.db.models.functions import Lower, Concat

import user
from scouting.models import ScoutAuthGroup
from user.models import User, PhoneType, Link


def get_users(active, admin):
    user_active = Q()
    if active in [-1, 1]:
        user_active = Q(is_active=active == 1)

    user_admin = Q()
    if not admin:
        group = Group.objects.get(name="Admin")
        user_admin = Q(groups__in=[group])

    users = (
        User.objects.annotate(name=Concat("first_name", Value(" "), "last_name"))
        .filter(user_active)
        .exclude(user_admin)
        .order_by("is_active", Lower("first_name"), Lower("last_name"))
    )

    # Q(date_joined__isnull=False) &

    return users


def save_user(data):
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


def get_user_groups(user_id: int):
    user_groups = User.objects.get(id=user_id).groups.all().order_by("name")

    return user_groups


"""
def get_all_user_groups(user_id: int = None):
    user_groups = Group.objects.all().order_by('name')

    return user_groups
"""


def get_phone_types():
    return PhoneType.objects.all().order_by("carrier")


def delete_phone_type(phone_type_id: int):
    phone_type = PhoneType.objects.get(id=phone_type_id)

    if phone_type.user_set.exists():
        raise ValueError("Can't delete, there are users tied to this phone type.")

    phone_type.delete()


def get_users_in_group(name: str):
    return get_users(1, 1).filter(groups__name=name)


def get_users_with_permission(codename: str):
    users = []
    prmsn = Permission.objects.get(codename=codename)
    users = get_users(1, 1).filter(
        groups__name__in=set(g.name for g in prmsn.group_set.all())
    )

    return users


def get_groups():
    return Group.objects.all().order_by("name")


def save_group(data):
    if data.get("id", None) is None:
        group = Group(name=data.get("name"))
    else:
        group = Group.objects.get(id=data.get("id", None))
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


def delete_group(group_id):
    try:
        ScoutAuthGroup.objects.get(group_id_id=group_id).delete()
    except ScoutAuthGroup.DoesNotExist as e:
        pass
    Group.objects.get(id=group_id).delete()


def get_permissions():
    return Permission.objects.filter(content_type_id=-1).order_by("name")


def save_permission(data):
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
