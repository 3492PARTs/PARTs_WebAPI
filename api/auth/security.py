from django.utils import timezone

from .models import *
from .serializers import RetMessageSerializer
from django.db.models import Q
from rest_framework.response import Response


def has_access(user_id, sec_permission):
    # how to use has_access(self.request.user.id, 36)

    auth_user_grps = AuthUserGroups.objects.filter(user=user_id)
    auth_grp_prmsns = AuthGroupPermissions.objects.filter(
        Q(group__in=[auth_grp.group.id for auth_grp in auth_user_grps]) & Q(permission=sec_permission))

    return auth_grp_prmsns.count() > 0


def get_user_permissions(user_id):
    auth_user_grps = AuthUserGroups.objects.filter(user=user_id)
    auth_grp_prmsns = AuthGroupPermissions.objects.filter(group__in=[auth_grp.group.id for auth_grp in auth_user_grps])

    return [prmsn.permission for prmsn in auth_grp_prmsns]


def get_user_groups(user_id):
    augs = AuthUserGroups.objects.filter(user=user_id)

    ags = []
    for aug in augs:
        ags.append(aug.group)

    return ags


def ret_message(message, error=False, location='', user_id=0, exception=None):
    # TODO Make all of these optional in the DB
    if error:
        user = AuthUser.objects.get(id=user_id)
        print('----------ERROR START----------')
        print('Error in: ' + location)
        print('Message: ' + message)
        print('Error by: ' + user.username + ' ' + user.first_name + ' ' + user.last_name)
        print('Exception: ')
        print(exception)
        print('----------ERROR END----------')
        ErrorLog(user=user, location=location, message=message, exception=exception, time=timezone.now(), void_ind='n').save()
    return Response(RetMessageSerializer({'retMessage': message, 'error': error}).data)
