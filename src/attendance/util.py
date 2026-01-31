from typing import Any
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, QuerySet
from django.db import transaction
from django.utils.timezone import now as timezone_now
from datetime import datetime, time
import pytz
from django.utils.timezone import localtime

from attendance.serializers import MeetingSerializer
from user.serializers import UserSerializer
from user.models import User
from attendance.models import Attendance, Meeting, AttendanceApprovalType, MeetingType
import scouting.util
import user.util


def get_meetings(id: int = None) -> QuerySet[Meeting] | Meeting:
    """
    Get all non-voided meetings for the current season.

    Returns:
        QuerySet of Meeting objects for the current season, ordered by start time and title or a single Meeting if id is provided
    """
    if id is not None:
        return Meeting.objects.get(id=id)
    return Meeting.objects.filter(
        Q(season=scouting.util.get_current_season()) & Q(void_ind="n")
    ).order_by("start", "title")


def save_meeting(meeting: dict[str, Any]) -> Meeting:
    """
    Create or update a meeting record.

    Args:
        meeting: Dictionary containing meeting data (id, title, description, start, end, meeting_typ, void_ind)
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
    m.meeting_typ = MeetingType.objects.get(
        meeting_typ=meeting["meeting_typ"]["meeting_typ"]
    )

    try:
        m.season
    except ObjectDoesNotExist:
        m.season = scouting.util.get_current_season()

    m.void_ind = meeting["void_ind"]

    m.save()
    return m


def get_meeting_hours() -> dict[float, float, float]:
    """
    Calculate total hours, bonus hours, and event hours from all meetings in the current season.

    Returns:
        Dictionary with 'hours' (regular meeting hours), 'bonus_hours' (bonus meeting hours),
        and 'event_hours' (event hours) keys

    Raises:
        Exception: If any meeting is missing an end time
    """

    # Get the current time in the default timezone
    # local_now = localtime().astimezone(pytz.timezone("America/New_York"))

    # Set midnight (00:00:00) of the current day in the local timezone
    # local_midnight = datetime.combine(
    #     local_now.date(), time.min, tzinfo=local_now.tzinfo
    # )
    # Convert it to UTC
    # utc_midnight = local_midnight.astimezone(pytz.utc)

    meetings = get_meetings()
    total_past = 0
    total_future = 0
    bonus = 0
    event = 0

    for meeting in meetings:
        if meeting.end is None:
            raise Exception("There is a meeting without an end time")

        diff = meeting.duration_hours()

        match meeting.meeting_typ.meeting_typ:
            case "reg":
                if meeting.ended:
                    total_past += diff
                else:
                    total_future += diff
            case "evnt":
                event += diff
            case "bns":
                bonus += diff

    return {
        "hours": round(total_past, 2),
        "hours_future": round(total_future, 2),
        "bonus_hours": round(bonus, 2),
        "event_hours": round(event, 2),
    }


def get_attendance_report(
    user_id: int | None = None, meeting_id: int | None = None
) -> list[dict[str, Any]]:
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

    all_hours = get_meeting_hours()
    total = all_hours["hours"]
    event_total = all_hours["event_hours"]

    ret = []

    for u in users:
        user_total = total
        attendance = get_attendance(u.id, meeting_id)
        reg_time = 0
        event_time = 0

        for att in attendance:
            # Exempt attendance reduces total required hours
            if att.is_exempt():
                user_total -= att.meeting.duration_hours()
            elif att.is_approved() and not att.absent:
                diff = att.duration_hours()

                if att.meeting is None:
                    reg_time += diff
                else:
                    match att.meeting.meeting_typ.meeting_typ:
                        case "reg":
                            reg_time += diff
                        case "bns":
                            reg_time += diff
                        case "evnt":
                            event_time += diff

        ret.append(
            {
                "user": u,
                "req_reg_time": round(user_total, 2),
                "reg_time": round(reg_time, 2),
                "reg_time_percentage": (
                    round(reg_time / user_total * 100, 0) if total != 0 else 0
                ),
                "event_time": round(event_time, 2),
                "event_time_percentage": (
                    round(event_time / event_total * 100, 0) if event_total != 0 else 0
                ),
            }
        )

    return ret


def get_attendance(
    user_id: int | None = None, meeting_id: int | None = None
) -> QuerySet[Attendance]:
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
    ).order_by("user__first_name", "user__last_name", "-time_in")


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


def end_meeting(meeting_id: int):
    """
    End a meeting by marking all users with no attendance record absent.

    Args:
        meeting_id: Specific meeting to end
    """
    with transaction.atomic():
        meeting = Meeting.objects.get(id=meeting_id)
        meeting.ended = True
        meeting.save()

        users = user.util.get_users(1, 0).filter(
            ~Q(id__in=meeting.attendance_set.filter(void_ind="n").values("user_id"))
        )

        for u in users:
            att = {
                "user": UserSerializer(u).data,
                "meeting": MeetingSerializer(meeting).data,
                "time_in": meeting.start,
                "absent": True,
                "approval_typ": {"approval_typ": "app"},
                "void_ind": "n",
            }
            save_attendance(att)
