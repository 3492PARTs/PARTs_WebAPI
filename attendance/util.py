from django.conf import settings

from django.db.models import Q

from user.models import User
from attendance.models import Attendance, Meeting
import scouting.util


def get_meetings():
    return Meeting.objects.filter(
        Q(season=scouting.util.get_current_season()) & Q(void_ind="n")
    )


def save_meeting(meeting):
    if meeting.get("id", None) is not None:
        m = Meeting.objects.get(id=meeting["id"])
    else:
        m = Meeting()

    m.title = meeting["title"]
    m.description = meeting["description"]
    m.start = meeting["start"]
    m.end = meeting["end"]
    m.void_ind = meeting["void_ind"]

    m.save()
    return m


def get_attendance(user_id=None):
    user = Q()
    if user_id is not None:
        user = Q(user__id=user_id)
    return Attendance.objects.filter(
        Q(user) & Q(void_ind="n") & (Q(meeting__isnull=True) | Q(meeting__void_ind="n"))
    )


def save_attendance(attendance):
    meeting = attendance.get("meeting", None)
    if meeting is not None:
        meeting = Meeting.objects.get(id=meeting["id"])

    if attendance.get("id", None) is not None:
        a = Attendance.objects.get(id=attendance["id"])
    else:
        a = Attendance()

    a.time_in = attendance["time_in"]
    a.time_out = attendance.get("time_out", None)
    a.absent = attendance["absent"]
    a.bonus_approved = attendance["bonus_approved"]
    a.approved = attendance["approved"]
    a.user = User.objects.get(id=attendance["user"]["id"])
    if meeting is not None:
        a.meeting = meeting
    a.void_ind = attendance["void_ind"]

    a.save()
    return a
