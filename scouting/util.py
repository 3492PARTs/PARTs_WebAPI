from django.db.models import Q, Case, When

from general.security import ret_message
from scouting.models import (
    Event,
    EventTeamInfo,
    Match,
    Schedule,
    ScheduleType,
    ScoutFieldSchedule,
    ScoutPit,
    Season,
    Team,
)


def get_all_seasons():
    return Season.objects.all().order_by("season")


def get_current_season():
    try:
        current_season = Season.objects.get(current="y")
        return current_season
    except Season.DoesNotExist as e:
        raise Exception("No season set, see an admin.")


def get_all_events():
    return Event.objects.filter(void_ind="n")


def get_current_event():
    try:
        event = Event.objects.get(Q(season=get_current_season()) & Q(current="y"))
        return event
    except Event.DoesNotExist as e:
        raise Exception("No event set, see an admin.")


def get_events(season: Season):
    event = Event.objects.filter(Q(season=season))

    return event


def get_current_teams():
    current_event = get_current_event()

    teams = (
        Team.objects.annotate(
            pit_result=Case(
                When(
                    team_no__in=ScoutPit.objects.filter(
                        Q(event=current_event) & Q(void_ind="n")
                    ).values_list("team_no", flat=True),
                    then=1,
                ),
                default=0,
            )
        )
        .filter(event=current_event)
        .order_by("team_no")
    )

    return teams


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


def get_current_scout_field_schedule():
    current_event = get_current_event()

    sfs = ScoutFieldSchedule.objects.filter(
        Q(event=current_event) & Q(void_ind="n")
    ).order_by("notification3", "st_time")

    return sfs


def get_current_scout_field_schedule_parsed():
    return list(
        parse_scout_field_schedule(s) for s in get_current_scout_field_schedule()
    )


def get_current_schedule():
    current_event = get_current_event()

    schs = Schedule.objects.filter(Q(event=current_event) & Q(void_ind="n")).order_by(
        "sch_typ", "notified", "st_time"
    )

    return schs


def get_current_schedule_parsed():
    return list(parse_schedule(s) for s in get_current_schedule())


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
        "red_one_check_in": s.red_one_check_in,
        "red_two_id": s.red_two,
        "red_two_check_in": s.red_two_check_in,
        "red_three_id": s.red_three,
        "red_three_check_in": s.red_three_check_in,
        "blue_one_id": s.blue_one,
        "blue_one_check_in": s.blue_one_check_in,
        "blue_two_id": s.blue_two,
        "blue_two_check_in": s.blue_two_check_in,
        "blue_three_id": s.blue_three,
        "blue_three_check_in": s.blue_three_check_in,
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


def get_matches(event: Event):

    matches = Match.objects.filter(Q(event=event) & Q(void_ind="n")).order_by(
        "comp_level__comp_lvl_order", "match_number"
    )

    parsed_matches = []
    for m in matches:
        parsed_matches.append(parse_match(m))

    return parsed_matches


def parse_match(m: Match):
    eti_blue_one = get_event_team_info(m.blue_one, m.event)
    eti_blue_two = get_event_team_info(m.blue_two, m.event)
    eti_blue_three = get_event_team_info(m.blue_three, m.event)

    eti_red_one = get_event_team_info(m.red_one, m.event)
    eti_red_two = get_event_team_info(m.red_two, m.event)
    eti_red_three = get_event_team_info(m.red_three, m.event)

    return {
        "match_id": m.match_id,
        "event_id": m.event.event_id,
        "match_number": m.match_number,
        "red_score": m.red_score,
        "blue_score": m.blue_score,
        "time": m.time,
        "blue_one": m.blue_one.team_no,
        "blue_one_rank": (None if eti_blue_one is None else eti_blue_one.rank),
        "blue_one_field_response": match_team_has_result(m, m.blue_one),
        "blue_two": m.blue_two.team_no,
        "blue_two_rank": (None if eti_blue_two is None else eti_blue_two.rank),
        "blue_two_field_response": match_team_has_result(m, m.blue_two),
        "blue_three": m.blue_three.team_no,
        "blue_three_rank": (None if eti_blue_three is None else eti_blue_three.rank),
        "blue_three_field_response": match_team_has_result(m, m.blue_three),
        "red_one": m.red_one.team_no,
        "red_one_rank": (None if eti_red_one is None else eti_red_one.rank),
        "red_one_field_response": match_team_has_result(m, m.red_one),
        "red_two": m.red_two.team_no,
        "red_two_rank": (None if eti_red_two is None else eti_red_two.rank),
        "red_two_field_response": match_team_has_result(m, m.red_two),
        "red_three": m.red_three.team_no,
        "red_three_rank": (None if eti_red_three is None else eti_red_three.rank),
        "red_three_field_response": match_team_has_result(m, m.red_three),
        "comp_level": m.comp_level,
        "scout_field_result": len(m.scoutfield_set.all()) > 0,
    }


def get_event_team_info(team: Team, event: Event):
    try:
        info = team.eventteaminfo_set.get(Q(event=event) & Q(void_ind="n"))
    except EventTeamInfo.DoesNotExist:
        info = None

    return info


def match_team_has_result(match: Match, team: Team) -> bool:
    return len(match.scoutfield_set.filter(Q(void_ind="n") & Q(team_no=team))) > 0


def get_scout_field_schedule(id):
    return ScoutFieldSchedule.objects.get(scout_field_sch_id=id)
