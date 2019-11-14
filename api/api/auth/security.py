from .models import *
from .serializers import RetMessageSerializer
from django.db.models import Q


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


def ret_message(message, error=False):
    return RetMessageSerializer({'retMessage': message, 'error': error})
