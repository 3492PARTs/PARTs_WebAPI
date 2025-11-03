from typing import Any
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, QuerySet

from user.models import User
from attendance.models import Attendance, Meeting, AttendanceApprovalType
import scouting.util
import user.util


def get_meetings() -> QuerySet[Meeting]:
    """
    Get all non-voided meetings for the current season.
    
    Returns:
        QuerySet of Meeting objects for the current season, ordered by start time and title
    """
    return Meeting.objects.filter(
        Q(season=scouting.util.get_current_season()) & Q(void_ind="n")
    ).order_by("start", "title")


def save_meeting(meeting: dict[str, Any]) -> Meeting:
    """
    Create or update a meeting record.
    
    Args:
        meeting: Dictionary containing meeting data (id, title, description, start, end, bonus, void_ind)
                If id is present, updates existing meeting; otherwise creates new one
                
    Returns:
        The created or updated Meeting object
    """
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


def get_meeting_hours() -> dict[str, float]:
    """
    Calculate total hours and bonus hours from all meetings in the current season.
    
    Returns:
        Dictionary with 'hours' (regular meeting hours) and 'bonus_hours' keys
        
    Raises:
        Exception: If any meeting is missing an end time
    """
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


def get_attendance_report(user_id: int | None = None, meeting_id: int | None = None) -> list[dict[str, Any]]:
    """
    Generate an attendance report showing hours and percentage for users.
    
    Args:
        user_id: If provided, generate report for specific user only
        meeting_id: If provided, filter attendance to specific meeting
        
    Returns:
        List of dictionaries containing user, time (hours), and percentage for each user
    """
    users = None
    if user_id is not None:
        users = User.objects.filter(id=user_id)
    else:
        users = user.util.get_users(1, 0 if settings.ENVIRONMENT == "main" else 1)

    total = get_meeting_hours()["hours"]

    ret = []

    for u in users:
        attendance = get_attendance(u.id, meeting_id)
        time = 0

        for att in attendance:
            if att.is_approved() and not att.absent:
                time += (att.time_out - att.time_in).total_seconds() / 3600

        ret.append(
            {
                "user": u,
                "time": round(time, 2),
                "percentage": round(time / total * 100, 0) if total != 0 else 0,
            }
        )

    return ret


def get_attendance(user_id: int | None = None, meeting_id: int | None = None) -> QuerySet[Attendance]:
    """
    Get attendance records filtered by user and/or meeting.
    
    Args:
        user_id: If provided, filter to specific user
        meeting_id: If provided, filter to specific meeting
        
    Returns:
        QuerySet of Attendance objects for current season matching the filters
    """
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
