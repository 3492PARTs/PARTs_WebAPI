from django.db.models import Q

from general.security import ret_message
from scouting.models import Event, Schedule, ScheduleType, ScoutFieldSchedule, Season


def get_current_season():
    try:
        current_season = Season.objects.get(current="y")
    except Season.DoesNotExist as e:
        current_season = None

    return current_season


def get_event(season: Season, current: str = None):
    try:
        current_event = Q()

        if current is not None:
            current_event = Q(current=current)

        event = Event.objects.get(Q(season=season) & current_event)
    except Event.DoesNotExist as e:
        event = None

    return event


def get_no_season_ret_message(endpoint: str, user_id: int):
    return ret_message("No season set, see an admin.", True, endpoint, user_id)


def get_no_event_ret_message(endpoint: str, user_id: int):
    return ret_message("No event set, see an admin.", True, endpoint, user_id)


def format_scout_field_schedule_entry(fs: ScoutFieldSchedule):
    return {
        "scout_field_sch_id": fs.scout_field_sch_id,
        "event_id": fs.event_id,
        "st_time": fs.st_time,
        "end_time": fs.end_time,
        "notification1": fs.notification1,
        "notification2": fs.notification2,
        "notification3": fs.notification3,
        "red_one_id": fs.red_one,
        "red_two_id": fs.red_two,
        "red_three_id": fs.red_three,
        "blue_one_id": fs.blue_one,
        "blue_two_id": fs.blue_two,
        "blue_three_id": fs.blue_three,
        "red_one_check_in": fs.red_one_check_in,
        "red_two_check_in": fs.red_two_check_in,
        "red_three_check_in": fs.red_three_check_in,
        "blue_one_check_in": fs.blue_one_check_in,
        "blue_two_check_in": fs.blue_two_check_in,
        "blue_three_check_in": fs.blue_three_check_in,
        "scouts": "R1: "
        + (
            ""
            if fs.red_one is None
            else fs.red_one.first_name + " " + fs.red_one.last_name[0:1]
        )
        + "\nR2: "
        + (
            ""
            if fs.red_two is None
            else fs.red_two.first_name + " " + fs.red_two.last_name[0:1]
        )
        + "\nR3: "
        + (
            ""
            if fs.red_three is None
            else fs.red_three.first_name + " " + fs.red_three.last_name[0:1]
        )
        + "\nB1: "
        + (
            ""
            if fs.blue_one is None
            else fs.blue_one.first_name + " " + fs.blue_one.last_name[0:1]
        )
        + "\nB2: "
        + (
            ""
            if fs.blue_two is None
            else fs.blue_two.first_name + " " + fs.blue_two.last_name[0:1]
        )
        + "\nB3: "
        + (
            ""
            if fs.blue_three is None
            else fs.blue_three.first_name + " " + fs.blue_three.last_name[0:1]
        ),
    }


def get_current_scout_field_schedule(request):
    current_season = get_current_season()

    if current_season is None:
        return get_no_season_ret_message(
            "scouting.util.get_current_scout_field_schedule", request.user.id
        )

    current_event = get_event(current_season, "y")

    if current_event is None:
        return get_no_event_ret_message(
            "scouting.util.get_current_scout_field_schedule", request.user.id
        )

    sfs = ScoutFieldSchedule.objects.filter(
        Q(event=current_event) & Q(void_ind="n")
    ).order_by("notification3", "st_time")

    return sfs


def get_current_schedule(request):
    current_season = get_current_season()

    if current_season is None:
        return get_no_season_ret_message(
            "scouting.util.get_current_scout_field_schedule", request.user.id
        )

    current_event = get_event(current_season, "y")

    if current_event is None:
        return get_no_event_ret_message(
            "scouting.util.get_current_scout_field_schedule", request.user.id
        )

    schs = Schedule.objects.filter(Q(event=current_event) & Q(void_ind="n")).order_by(
        "sch_typ", "notified", "st_time"
    )

    return schs


def get_schedule_types():
    return ScheduleType.objects.all().order_by("sch_nm")


def parse_scout_field_schedule(s: ScoutFieldSchedule):
    return {
        "scout_field_sch_id": s.scout_field_sch_id,
        "event_id": s.event_id,
        "st_time": s.st_time,
        "end_time": s.end_time,
        "notification1": s.notification1,
        "notification2": s.notification2,
        "notification3": s.notification3,
        "red_one_id": s.red_one,
        "red_two_id": s.red_two,
        "red_three_id": s.red_three,
        "blue_one_id": s.blue_one,
        "blue_two_id": s.blue_two,
        "blue_three_id": s.blue_three,
        "scouts": "R1: "
        + (
            ""
            if s.red_one is None
            else s.red_one.first_name + " " + s.red_one.last_name[0:1]
        )
        + "\nR2: "
        + (
            ""
            if s.red_two is None
            else s.red_two.first_name + " " + s.red_two.last_name[0:1]
        )
        + "\nR3: "
        + (
            ""
            if s.red_three is None
            else s.red_three.first_name + " " + s.red_three.last_name[0:1]
        )
        + "\nB1: "
        + (
            ""
            if s.blue_one is None
            else s.blue_one.first_name + " " + s.blue_one.last_name[0:1]
        )
        + "\nB2: "
        + (
            ""
            if s.blue_two is None
            else s.blue_two.first_name + " " + s.blue_two.last_name[0:1]
        )
        + "\nB3: "
        + (
            ""
            if s.blue_three is None
            else s.blue_three.first_name + " " + s.blue_three.last_name[0:1]
        ),
    }


def parse_schedule(s: Schedule):
    return {
        "sch_id": s.sch_id,
        "sch_typ": s.sch_typ.sch_typ,
        "sch_nm": s.sch_typ.sch_nm,
        "event_id": s.event.event_id,
        "st_time": s.st_time,
        "end_time": s.end_time,
        "notified": s.notified,
        "user": s.user,
        "user_name": s.user.get_full_name(),
    }
