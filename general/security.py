import traceback
from django.utils import timezone

import user.util
from admin.models import ErrorLog
from user.serializers import RetMessageSerializer
from rest_framework.response import Response
from user.models import User


def has_access(user_id, sec_permission):
    # how to use has_access(self.request.user.id, 36)
    prmsns = get_user_permissions(user_id)

    access = False
    for prmsn in prmsns:
        if prmsn.codename == sec_permission:
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

    return augs


def ret_message(message, error=False, path="", user_id=-1, exception=None):
    # TODO Make all of these optional in the DB
    if error:
        print("----------ERROR START----------")

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            user = User.objects.get(id=-1)
            err_msg = "Ran into DoesNotExist exception finding user"
            print(err_msg)
            message += f"\n{err_msg}\n"

        tb = traceback.format_exc()

        tb = (tb[:75] + "..") if len(tb) > 75 else tb

        print("Error in: " + path)
        print("Message: " + message)
        print(
            "Error by: " + user.username + " " + user.first_name + " " + user.last_name
        )
        print("Exception: ")
        print(exception)

        print("TraceBack: ")
        print(tb)

        print("----------ERROR END----------")

        try:
            ErrorLog(
                user=user,
                path=path,
                message=message,
                exception=exception,
                traceback=tb,
                time=timezone.now(),
                void_ind="n",
            ).save()
        except Exception as e:
            message += "\nCritical Error: please email the team admin at team3492@gmail.com\nSend them this message:\n"
            message += e
            try:
                ErrorLog(
                    user=User.objects.get(id=-1),
                    path="general.security.ret_message",
                    message=message,
                    exception=e,
                    time=timezone.now(),
                    void_ind="n",
                ).save()
            except Exception as e:
                print("The most fatal of errors nothing was logged in db")
                print("Exception: ")
                print(e)

            return Response(
                RetMessageSerializer({"retMessage": message, "error": error}).data
            )
    return Response(RetMessageSerializer({"retMessage": message, "error": error}).data)
