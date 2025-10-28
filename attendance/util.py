from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from django.db.models import Q

from user.models import User
from attendance.models import Attendance, Meeting, AttendanceApprovalType
import scouting.util


def get_meetings():
    return Meeting.objects.filter(
        Q(season=scouting.util.get_current_season()) & Q(void_ind="n")
    ).order_by("start", "title")


def save_meeting(meeting):
    if meeting.get("id", None) is not None:
        m = Meeting.objects.get(id=meeting["id"])
    else:
        m = Meeting()

    m.title = meeting["title"]
    m.description = meeting["description"]
    m.start = meeting["start"]
    m.end = meeting["end"]
    m.bonus = meeting["bonus"]

    try:
        m.season
    except ObjectDoesNotExist:
        m.season = scouting.util.get_current_season()

    m.void_ind = meeting["void_ind"]

    m.save()
    return m


def get_meeting_hours():
    meetings = get_meetings()
    total = 0
    bonus = 0
    for meeting in meetings:
        if meeting.end is None:
            raise Exception("There is a meeting without an end time")

        diff = (meeting.end - meeting.start).total_seconds() / 3600
        if meeting.bonus:
            bonus += diff
        else:
            total += diff

    return {"hours": round(total, 2), "bonus_hours": round(bonus, 2)}


def get_attendance_report(user_id=None, meeting_id=None):
    users = None
    if user_id is not None:
        users = User.objects.filter(id=user_id)
    else:
        users = User.objects.filter(is_active=True).order_by("first_name", "last_name")

    total = get_meeting_hours()["hours"]

    ret = []

    for user in users:
        attendance = get_attendance(user.id, meeting_id)
        time = 0

        for att in attendance:
            if att.is_approved() and not att.absent:
                time += (att.time_out - att.time_in).total_seconds() / 3600

        ret.append(
            {
                "user": user,
                "time": round(time, 2),
                "percentage": round(time / total * 100, 2),
            }
        )

    return ret


def get_attendance(user_id=None, meeting_id=None):
    user = Q()
    if user_id is not None:
        user = Q(user__id=user_id)

    meeting = Q()
    if meeting_id is not None:
        meeting = Q(meeting__id=meeting_id)

    return Attendance.objects.filter(
        user
        & meeting
        & Q(season=scouting.util.get_current_season())
        & (Q(meeting__isnull=True) | Q(meeting__void_ind="n"))
        & Q(void_ind="n")
    ).order_by("-time_in", "user__first_name", "user__last_name")


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

    if attendance.get("approval_typ", None) is not None:
        a.approval_typ = AttendanceApprovalType.objects.get(
            approval_typ=attendance["approval_typ"]["approval_typ"]
        )
    else:
        a.approval_typ = AttendanceApprovalType.objects.get(approval_typ="unapp")

    a.user = User.objects.get(id=attendance["user"]["id"])

    if a.absent:
        a.approval_typ = AttendanceApprovalType.objects.get(approval_typ="app")

    if meeting is not None:
        a.meeting = meeting

    try:
        a.season
    except ObjectDoesNotExist:
        a.season = scouting.util.get_current_season()

    a.void_ind = attendance["void_ind"]

    if a.void_ind != "y" and not a.absent and a.is_approved() and a.time_out is None:
        raise Exception("Cannot approve if no time out.")

    a.save()
    return a
