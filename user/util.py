from django.contrib.auth.models import Group
from django.db.models import Q, Value
from django.db.models.functions import Lower, Concat

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


def get_all_user_groups(user_id: int = None):
    user_groups = Group.objects.all().order_by('name')

    return user_groups


def get_phone_types():
    return PhoneType.objects.all().order_by('carrier')


def get_users_in_group(name: str):
    return get_users(1).filter(groups__name=name)
