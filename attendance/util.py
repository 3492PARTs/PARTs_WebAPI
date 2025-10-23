import django
from django.conf import settings

from django.db import transaction
from django.db.models import Q

from attendance.models import Attendance


def get_attendance():
    Attendance.objects.get()


def save_attendance(attendance):
    if attendance.get("id", None) is not None:
        a = attendance.objects.get(id=attendance["id"])
        a.time = attendance["time"]
        a.user.id = attendance["user"]["id"]
    else:
        a = Attendance(
            time=attendance["time"], user_id=attendance["user"]["id"], void_ind="n"
        )

    a.save()
    return a
