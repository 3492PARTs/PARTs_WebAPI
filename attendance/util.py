from django.conf import settings

from django.db import transaction
from django.db.models import Q

from attendance.models import Attendance, Meeting
import scouting.util


def get_meetings():
    return Meeting.objects.filter(
        Q(season=scouting.util.get_current_season()) & Q(void_ind="n")
    )


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
    return Attendance.objects.filter(Q(void_ind="n"))


def save_attendance(attendance):
    meeting = attendance.get("meeting", None)
    if meeting is not None:
        meeting = meeting["id"]

    if attendance.get("id", None) is not None:
        a = Attendance.objects.get(id=attendance["id"])
        a.time_in = attendance["time_in"]
        a.time_out = attendance.get("time_out", None)
        a.absent = attendance["absent"]
        a.bonus_approved = attendance["bonus_approved"]
        a.user.id = attendance["user"]["id"]
        if meeting is not None:
            a.meeting.id = meeting
        a.void_ind = attendance["void_ind"]
    else:
        a = Attendance(
            time_in=attendance["time_in"],
            time_out=attendance.get("time_out", None),
            absent=attendance["absent"],
            bonus_approved=attendance["bonus_approved"],
            user_id=attendance["user"]["id"],
            meeting_id=meeting,
            void_ind="n",
        )

    a.save()
    return a
