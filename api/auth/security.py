from django.utils import timezone

from .models import *
from .serializers import RetMessageSerializer
from django.db.models import Q
from rest_framework.response import Response
from django.contrib.auth.models import User, Permission


def has_access(user_id, sec_permission):
    # how to use has_access(self.request.user.id, 36)
    prmsns = get_user_permissions(user_id)

    access = False
    for prmsn in prmsns:
        if prmsn.id == sec_permission:
            access = True
            break

    return access


def get_user_permissions(user_id):
    user = User.objects.get(id=user_id)
    user_groups = user.groups.all()

    prmsns = []
    for grp in user_groups:
        for prmsn in grp.permissions.all():
            prmsns.append(prmsn)

    return prmsns


def get_user_groups(user_id):
    user = User.objects.get(id=user_id)

    augs = user.groups.all()

    ags = []
    for aug in augs:
        ags.append(aug)

    return ags


def ret_message(message, error=False, path='', user_id=0, exception=None):
    # TODO Make all of these optional in the DB
    if error:
        user = User.objects.get(id=user_id)
        print('----------ERROR START----------')
        print('Error in: ' + path)
        print('Message: ' + message)
        print('Error by: ' + user.username + ' ' + user.first_name + ' ' + user.last_name)
        print('Exception: ')
        print(exception)
        print('----------ERROR END----------')
        ErrorLog(user=user, path=path, message=message, exception=exception,
                 time=timezone.now(), void_ind='n').save()
    return Response(RetMessageSerializer({'retMessage': message, 'error': error}).data)
