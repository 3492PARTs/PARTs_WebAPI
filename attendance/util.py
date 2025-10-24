import django
from django.conf import settings

from django.db import transaction
from django.db.models import Q

from attendance.models import Attendance, Meeting


def get_meetings():
    return Meeting.objects.all()


def save_meeting(meeting):
    if meeting.get("id", None) is not None:
        m = Meeting.objects.get(id=meeting["id"])
        m.title = meeting["title"]
        m.description = meeting["description"]
        m.start = meeting["start"]
        m.end = meeting["end"]
    else:
        m = Meeting(
            start=meeting["start"],
            end=meeting["end"],
            title=meeting["title"],
            description=meeting["description"],
            void_ind="n",
        )

    m.save()
    return m


def get_attendance():
    return Attendance.objects.all()


def save_attendance(attendance):
    if attendance.get("id", None) is not None:
        a = attendance.objects.get(id=attendance["id"])
        a.time_in = attendance["time_in"]
        a.time_out = attendance["time_out"]
        a.absent = attendance["absent"]
        a.bonus_approved = attendance["bonus_approved"]
        a.user.id = attendance["user"]["id"]
        a.meeting.id = attendance["meeting"]["id"]
    else:
        a = Attendance(
            time_in=attendance["time_in"],
            time_out=attendance["time_out"],
            absent=attendance["absent"],
            bonus_approved=attendance["bonus_approved"],
            user_id=attendance["user"]["id"],
            meeting_id=attendance["meeting"]["id"],
            void_ind="n",
        )

    a.save()
    return a
