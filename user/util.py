from django.contrib.auth.models import Group, Permission
from django.db.models import Q, Value, Count
from django.db.models.functions import Lower, Concat

import user
from scouting.models import ScoutAuthGroups
from user.models import User, PhoneType


def get_users(active, admin):
    user_active = Q()
    if active in [-1, 1]:
        user_active = Q(is_active=active == 1)

    user_admin = Q()
    if not admin:
        group = Group.objects.get(name='Admin')
        user_admin = Q(groups__in=[group])

    users = (User.objects.annotate(name=Concat('first_name', Value(' '), 'last_name'))
             .filter(Q(date_joined__isnull=False) & user_active).exclude(user_admin)
             .order_by('is_active', Lower('first_name'), Lower('last_name')))

    return users


def save_user(data):
    groups = []
    user = User.objects.get(username=data['user']['username'])
    user.first_name = data['user']['first_name']
    user.last_name = data['user']['last_name']
    user.email = data['user']['email'].lower()
    user.discord_user_id = data['user']['discord_user_id']
    user.phone = data['user']['phone']
    user.phone_type_id = data['user'].get('phone_type_id', None)
    user.is_active = data['user']['is_active']
    user.save()

    if 'groups' in data:
        for d in data['groups']:
            groups.append(d['name'])
            aug = user.groups.filter(name=d['name']).exists()
            if not aug:
                group = Group.objects.get(name=d['name'])
                user.groups.add(group)

        user_groups = user.groups.filter(~Q(name__in=groups))

        for user_group in user_groups:
            user_group.user_set.remove(user)

    return user


def get_user_groups(user_id: int):
    user_groups = User.objects.get(id=user_id).groups.all().order_by('name')

    return user_groups

"""
def get_all_user_groups(user_id: int = None):
    user_groups = Group.objects.all().order_by('name')

    return user_groups
"""

def get_phone_types():
    return PhoneType.objects.all().order_by('carrier')


def get_users_in_group(name: str):
    return get_users(1, 1).filter(groups__name=name)


def get_users_with_permission(codename: str):
    users = []
    prmsn = Permission.objects.get(codename=codename)
    users = get_users(1, 1).filter(groups__name__in=set(g.name for g in prmsn.group_set.all()))

    return users


def get_groups():
    return Group.objects.all().order_by('name')


def save_group(data):
    if data.get('id', None) is None:
        group = Group(name=data.get('name'))
    else:
        group = Group.objects.get(id=data.get('id', None))
        group.name = data.get('name')

    group.save()

    prmsn_ids = []
    for prm in data.get('permissions', []):
        prmsn_ids.append(prm['id'])
        gpr_prmsn = group.permissions.filter(id=prm['id']).exists()
        if not gpr_prmsn:
            permission = Permission.objects.get(id=prm['id'])
            group.permissions.add(permission)

    gpr_prmsns = group.permissions.filter(~Q(id__in=prmsn_ids))

    for gpr_prmsn in gpr_prmsns:
        gpr_prmsn.group_set.remove(group)


def delete_group(group_id):
    ScoutAuthGroups.objects.get(auth_group_id_id=group_id).delete()
    Group.objects.get(id=group_id).delete()


def get_permissions():
    return Permission.objects.filter(content_type_id=-1).order_by('name')


def save_permission(data):
    if data.get('id', None) is None:
        prmsn = Permission(name=data['name'])
    else:
        prmsn = Permission.objects.get(id=data['id'])
        prmsn.name = data['name']

    prmsn.codename = data['codename']
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