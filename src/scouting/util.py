from typing import Any
from django.db.models import Q, Case, When, OuterRef, Subquery, Exists, QuerySet

import general.cloudinary
from scouting.models import (
    Event,
    EventTeamInfo,
    Match,
    Schedule,
    ScheduleType,
    FieldSchedule,
    PitResponse,
    Season,
    Team,
    FieldForm,
    FieldResponse,
    UserInfo,
)
from user.models import User


def get_all_seasons() -> QuerySet[Season]:
    """
    Get all seasons ordered by year.
    
    Returns:
        QuerySet of all Season objects ordered by season year
    """
    return Season.objects.all().order_by("season")


def get_season(year: str) -> Season:
    """
    Get a specific season by year.
    
    Args:
        year: The year of the season (e.g., "2024")
        
    Returns:
        The Season object for the specified year
    """
    return Season.objects.get(season=year)


def get_or_create_season(year: str) -> Season:
    """
    Get an existing season or create a new one if it doesn't exist.
    
    Args:
        year: The year of the season (e.g., "2024")
        
    Returns:
        The Season object (existing or newly created)
    """
    try:
        season = Season.objects.get(season=year)
    except Season.DoesNotExist:
        season = Season(season=year, current="n")
        season.save()

    return season


def get_current_season() -> Season:
    """
    Get the currently active season.
    
    Returns:
        The current Season object
        
    Raises:
        Exception: If no season is set as current
    """
    try:
        current_season = Season.objects.get(current="y")
        return current_season
    except Season.DoesNotExist as e:
        raise Exception("No season set, see an admin.")


def get_all_events() -> QuerySet[Event]:
    """
    Get all non-voided events.
    
    Returns:
        QuerySet of Event objects that are not voided
    """
    return Event.objects.filter(void_ind="n")


def get_current_event() -> Event:
    """
    Get the currently active event.
    
    Returns:
        The current Event object
        
    Raises:
        Exception: If no event is set as current for the current season
    """
    try:
        event = Event.objects.get(Q(season=get_current_season()) & Q(current="y"))
        return event
    except Event.DoesNotExist as e:
        raise Exception("No event set, see an admin.")


def get_event(event_cd: str) -> Event:
    """
    Get a specific event by its event code.
    
    Args:
        event_cd: The event code
        
    Returns:
        The Event object with the specified code
    """
    event = Event.objects.get(event_cd=event_cd)

    return event


def get_events(season: Season) -> QuerySet[Event]:
    """
    Get all events for a specific season.
    
    Args:
        season: The Season object to get events for
        
    Returns:
        QuerySet of Event objects for the specified season
    """
    event = Event.objects.filter(Q(season=season))

    return event


def get_teams(current: bool) -> list[dict[str, Any]]:
    """
    Get teams, optionally filtered to the current event.
    
    Args:
        current: If True, only return teams at the current event
        
    Returns:
        List of dictionaries containing parsed team information
    """
    current_event = get_current_event()

    q_current_event = Q()
    if current:
        q_current_event = Q(event=current_event)

    teams = (
        Team.objects.annotate(
            pit_result=Case(
                When(
                    team_no__in=PitResponse.objects.filter(
                        Q(event=current_event) & Q(void_ind="n")
                    ).values_list("team_id", flat=True),
                    then=1,
                ),
                default=0,
            )
        )
        .filter(q_current_event)
        .order_by("team_no")
    )

    return [parse_team(team) for team in teams]


def parse_team(in_team: Team, checked: bool = False) -> dict[str, Any]:
    """
    Parse a Team object into a dictionary with event-specific information.
    
    Args:
        in_team: The Team object to parse
        checked: Whether the team is checked/selected
        
    Returns:
        Dictionary containing team number, name, checked status, pit result, and rank
    """
    eti = get_event_team_info(in_team, get_current_event())
    return {
        "team_no": in_team.team_no,
        "team_nm": in_team.team_nm,
        "checked": checked,
        "pit_result": (
            in_team.pit_result
            if getattr(in_team, "pit_result", None) is not None
            else None
        ),
        "rank": eti.rank if eti is not None else None,
    }


def format_scout_field_schedule_entry(fs: FieldSchedule) -> dict[str, Any]:
    """
    Format a FieldSchedule object into a dictionary with detailed scout assignments.
    
    Args:
        fs: The FieldSchedule object to format
        
    Returns:
        Dictionary containing schedule details including scout assignments for all positions
    """
    return {
        "id": fs.id,
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


def get_current_scout_field_schedule() -> QuerySet[FieldSchedule]:
    """
    Get all field scouting schedules for the current event.
    
    Returns:
        QuerySet of FieldSchedule objects ordered by notification status and start time
    """
    current_event = get_current_event()

    sfs = FieldSchedule.objects.filter(
        Q(event=current_event) & Q(void_ind="n")
    ).order_by("notification3", "st_time")

    return sfs


def get_current_scout_field_schedule_parsed() -> list[dict[str, Any]]:
    """
    Get parsed field scouting schedules for the current event.
    
    Returns:
        List of dictionaries with parsed schedule information
    """
    return list(
        parse_scout_field_schedule(s) for s in get_current_scout_field_schedule()
    )


def get_current_schedule() -> QuerySet[Schedule]:
    """
    Get all schedules for the current event.
    
    Returns:
        QuerySet of Schedule objects ordered by type, notification status, and start time
    """
    current_event = get_current_event()

    schs = Schedule.objects.filter(Q(event=current_event) & Q(void_ind="n")).order_by(
        "sch_typ", "notified", "st_time"
    )

    return schs


def get_current_schedule_parsed() -> list[dict[str, Any]]:
    """
    Get parsed schedules for the current event.
    
    Returns:
        List of dictionaries with parsed schedule information
    """
    return list(parse_schedule(s) for s in get_current_schedule())


def get_schedule_types() -> QuerySet[ScheduleType]:
    """
    Get all available schedule types.
    
    Returns:
        QuerySet of ScheduleType objects ordered by schedule name
    """
    return ScheduleType.objects.all().order_by("sch_nm")


def get_group_leader_user(user: User | None) -> User | None:
    """
    Check if a user is a group leader in scouting.
    
    Args:
        user: The User object to check
        
    Returns:
        The User object if they are a group leader, None otherwise
    """
    try:
        if user is None:
            return None

        u = user.scouting_user_info.get(Q(void_ind="n") & Q(group_leader=True))
        return user
    except UserInfo.DoesNotExist:
        return None


def parse_scout_field_schedule(s: FieldSchedule) -> dict[str, Any]:
    """
    Parse a FieldSchedule object into a detailed dictionary.
    
    Args:
        s: The FieldSchedule object to parse
        
    Returns:
        Dictionary with schedule details including group leaders and scout assignments
    """

    red_leader = get_group_leader_user(s.red_one)
    if red_leader is None:
        red_leader = get_group_leader_user(s.red_two)
    if red_leader is None:
        red_leader = get_group_leader_user(s.red_three)

    blue_leader = get_group_leader_user(s.blue_one)
    if blue_leader is None:
        blue_leader = get_group_leader_user(s.blue_two)
    if blue_leader is None:
        blue_leader = get_group_leader_user(s.blue_three)

    return {
        "id": s.id,
        "event_id": s.event_id,
        "st_time": s.st_time,
        "end_time": s.end_time,
        "notification1": s.notification1,
        "notification2": s.notification2,
        "notification3": s.notification3,
        "red_leader": red_leader,
        "red_one_id": s.red_one,
        "red_one_check_in": s.red_one_check_in,
        "red_two_id": s.red_two,
        "red_two_check_in": s.red_two_check_in,
        "red_three_id": s.red_three,
        "red_three_check_in": s.red_three_check_in,
        "blue_leader": blue_leader,
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
        "id": s.id,
        "sch_typ": s.sch_typ.sch_typ,
        "sch_nm": s.sch_typ.sch_nm,
        "event_id": s.event.id,
        "st_time": s.st_time,
        "end_time": s.end_time,
        "notified": s.notified,
        "user": s.user,
        "user_name": s.user.get_full_name(),
    }


def get_matches(event: Event):

    matches = (
        Match.objects.annotate(
            blue_one_rank=Subquery(rank_query("blue_one")),
            blue_two_rank=Subquery(rank_query("blue_two")),
            blue_three_rank=Subquery(rank_query("blue_three")),
            red_one_rank=Subquery(rank_query("red_one")),
            red_two_rank=Subquery(rank_query("red_two")),
            red_three_rank=Subquery(rank_query("red_three")),
            blue_one_field_response=Exists(field_response_query("blue_one")),
            blue_two_field_response=Exists(field_response_query("blue_two")),
            blue_three_field_response=Exists(field_response_query("blue_three")),
            red_one_field_response=Exists(field_response_query("red_one")),
            red_two_field_response=Exists(field_response_query("red_two")),
            red_three_field_response=Exists(field_response_query("red_three")),
        )
        # .prefetch_related("event", "blue_one", "blue_two", "blue_three", "red_one", "red_two", "red_three",
        #                  "fieldresponse_set",
        #                  "blue_one__eventteaminfo_set", "blue_two__eventteaminfo_set", "blue_three__eventteaminfo_set", "red_one__eventteaminfo_set", "red_two__eventteaminfo_set", "red_three__eventteaminfo_set")
        .filter(Q(event=event) & Q(void_ind="n")).order_by(
            "comp_level__comp_lvl_order", "match_number"
        )
    )

    parsed_matches = []
    for m in matches:
        parsed_matches.append(parse_match(m))

    return parsed_matches


def parse_match(in_match: Match):
    # print (in_match)
    blue_one_rank = get_rank(
        in_match.blue_one, in_match.event, getattr(in_match, "blue_one_rank", None)
    )
    blue_two_rank = get_rank(
        in_match.blue_two, in_match.event, getattr(in_match, "blue_two_rank", None)
    )
    blue_three_rank = get_rank(
        in_match.blue_three, in_match.event, getattr(in_match, "blue_three_rank", None)
    )
    red_one_rank = get_rank(
        in_match.red_one, in_match.event, getattr(in_match, "red_one_rank", None)
    )
    red_two_rank = get_rank(
        in_match.red_two, in_match.event, getattr(in_match, "red_two_rank", None)
    )
    red_three_rank = get_rank(
        in_match.red_three, in_match.event, getattr(in_match, "red_three_rank", None)
    )

    blue_one_field_response = get_match_team_has_response(
        in_match, in_match.blue_one, getattr(in_match, "blue_one_field_response", None)
    )
    blue_two_field_response = get_match_team_has_response(
        in_match, in_match.blue_two, getattr(in_match, "blue_two_field_response", None)
    )
    blue_three_field_response = get_match_team_has_response(
        in_match,
        in_match.blue_three,
        getattr(in_match, "blue_three_field_response", None),
    )
    red_one_field_response = get_match_team_has_response(
        in_match, in_match.red_one, getattr(in_match, "red_one_field_response", None)
    )
    red_two_field_response = get_match_team_has_response(
        in_match, in_match.red_two, getattr(in_match, "red_two_field_response", None)
    )
    red_three_field_response = get_match_team_has_response(
        in_match,
        in_match.red_three,
        getattr(in_match, "red_three_field_response", None),
    )

    return {
        "match_key": in_match.match_key,
        "event": in_match.event,
        "match_number": in_match.match_number,
        "red_score": in_match.red_score,
        "blue_score": in_match.blue_score,
        "time": in_match.time,
        "blue_one_id": in_match.blue_one_id,
        "blue_one_rank": blue_one_rank,
        "blue_one_field_response": blue_one_field_response,
        "blue_two_id": in_match.blue_two_id,
        "blue_two_rank": blue_two_rank,
        "blue_two_field_response": blue_two_field_response,
        "blue_three_id": in_match.blue_three_id,
        "blue_three_rank": blue_three_rank,
        "blue_three_field_response": blue_three_field_response,
        "red_one_id": in_match.red_one_id,
        "red_one_rank": red_one_rank,
        "red_one_field_response": red_one_field_response,
        "red_two_id": in_match.red_two_id,
        "red_two_rank": red_two_rank,
        "red_two_field_response": red_two_field_response,
        "red_three_id": in_match.red_three_id,
        "red_three_rank": red_three_rank,
        "red_three_field_response": red_three_field_response,
        "comp_level": in_match.comp_level,
        "scout_field_result": len(in_match.fieldresponse_set.all()) > 0,
    }


def rank_query(outer_ref: str):
    return EventTeamInfo.objects.filter(
        Q(event=OuterRef("event")) & Q(void_ind="n") & Q(team=OuterRef(outer_ref))
    ).values("rank")[:1]


def field_response_query(outer_ref):
    return FieldResponse.objects.filter(
        Q(void_ind="n")
        & Q(team=OuterRef(outer_ref))
        & Q(event=OuterRef("event"))
        & Q(match_id=OuterRef("pk"))
    )


def get_rank(team: Team, event: Event, rank=None):
    if rank is None:
        eti = get_event_team_info(team, event)
        rank = None if eti is None else eti.rank

    return rank


def get_match_team_has_response(match: Match, team: Team, has_response=None):
    if has_response is None:
        return match_team_has_result(match, team)

    return has_response


def get_event_team_info(team: Team, event: Event):
    try:
        info = team.eventteaminfo_set.get(Q(event=event) & Q(void_ind="n"))
    except EventTeamInfo.DoesNotExist:
        info = None

    return info


def match_team_has_result(match: Match, team: Team) -> bool:
    return len(match.fieldresponse_set.filter(Q(void_ind="n") & Q(team=team))) > 0


def get_scout_field_schedule(id):
    return FieldSchedule.objects.get(id=id)


def get_field_form():
    season = get_current_season()
    try:
        field_form = FieldForm.objects.get(Q(season=season) & Q(void_ind="n"))

        parsed_ff = {
            "id": field_form.id,
            "season_id": field_form.season.id,
            "img_url": general.cloudinary.build_image_url(
                field_form.img_id, field_form.img_ver
            ),
            "inv_img_url": general.cloudinary.build_image_url(
                field_form.inv_img_id, field_form.inv_img_ver
            ),
            "full_img_url": general.cloudinary.build_image_url(
                field_form.full_img_id, field_form.full_img_ver
            ),
        }
    except FieldForm.DoesNotExist as dne:
        parsed_ff = {}

    return parsed_ff
