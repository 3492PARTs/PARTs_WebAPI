from ast import Match
import datetime
import json
from django.conf import settings
from django.db import IntegrityError
from django.db.models import Q
import pytz
import requests

from form.models import Question, QuestionAnswer
from general.security import ret_message
import scouting
from scouting.models import (
    CompetitionLevel,
    Event,
    EventTeamInfo,
    Schedule,
    ScoutAuthGroups,
    ScoutField,
    ScoutFieldSchedule,
    ScoutPit,
    Season,
    Team,
    TeamNotes,
    Match,
    UserInfo,
)
import scouting.util
import scouting.models
import alerts.util
import user.util


def delete_event(event_id):
    e = Event.objects.get(event_id=event_id)

    teams_at_event = Team.objects.filter(event=e)
    for t in teams_at_event:
        t.event_set.remove(e)

    scout_fields = ScoutField.objects.filter(event=e)
    for sf in scout_fields:
        scout_field_answers = QuestionAnswer.objects.filter(response=sf.response)
        for sfa in scout_field_answers:
            sfa.delete()
        sf.delete()
        sf.response.delete()

    scout_pits = ScoutPit.objects.filter(event=e)
    for sp in scout_pits:
        scout_pit_answers = QuestionAnswer.objects.filter(response=sp.response)
        for spa in scout_pit_answers:
            spa.delete()

        for spi in sp.scoutpitimage_set.all():
            spi.delete()

        sp.delete()
        sp.response.delete()

    matches = Match.objects.filter(event=e)
    for m in matches:
        m.delete()

    scout_field_schedules = ScoutFieldSchedule.objects.filter(event=e)
    for sfs in scout_field_schedules:
        sfs.delete()

    schedules = Schedule.objects.filter(event=e)
    for s in schedules:
        s.delete()

    notes = TeamNotes.objects.filter(event=e)
    for n in notes:
        n.delete()

    event_team_infos = EventTeamInfo.objects.filter(event=e)
    for eti in event_team_infos:
        eti.delete()

    e.delete()

    return ret_message("Successfully deleted event: " + e.event_nm)


def get_scout_auth_groups():
    sags = ScoutAuthGroups.objects.all().order_by("auth_group_id__name")

    groups = list(sag.auth_group_id for sag in sags)

    return groups


def sync_season(season_id):
    season = Season.objects.get(season_id=season_id)

    r = requests.get(
        "https://www.thebluealliance.com/api/v3/team/frc3492/events/"
        + str(season.season),
        headers={"X-TBA-Auth-Key": settings.TBA_KEY},
    )
    r = json.loads(r.text)

    messages = ""
    for e in r:
        messages += scouting.admin.util.load_event(e)

    return messages


def sync_event(event_cd: str):
    r = requests.get(
        "https://www.thebluealliance.com/api/v3/event/" + event_cd,
        headers={"X-TBA-Auth-Key": settings.TBA_KEY},
    )
    r = json.loads(r.text)

    if r.get("Error", None) is not None:
        raise Exception(r["Error"])

    insert = []
    season = Season.objects.get(season=e["year"])
    time_zone = (
        e.get("timezone") if e.get("timezone", None) is not None else "America/New_York"
    )
    event_ = {
        "event_nm": e["name"],
        "date_st": datetime.datetime.strptime(e["start_date"], "%Y-%m-%d").astimezone(
            pytz.timezone(time_zone)
        ),
        "date_end": datetime.datetime.strptime(e["end_date"], "%Y-%m-%d").astimezone(
            pytz.timezone(time_zone)
        ),
        "event_cd": e["key"],
        "event_url": e.get("event_url", None),
        "gmaps_url": e.get("gmaps_url", None),
        "address": e.get("address", None),
        "city": e.get("city", None),
        "state_prov": e.get("state_prov", None),
        "postal_code": e.get("postal_code", None),
        "location_name": e.get("location_name", None),
        "timezone": e.get("timezone", "America/New_York"),
        "webcast_url": e["webcasts"][0]["channel"] if len(e["webcasts"]) > 0 else "",
        "teams": [],
        "teams_to_keep": [],
    }

    s = requests.get(
        "https://www.thebluealliance.com/api/v3/event/" + e["key"] + "/teams",
        headers={"X-TBA-Auth-Key": settings.TBA_KEY},
    )
    s = json.loads(s.text)

    for t in s:
        event_["teams"].append({"team_no": t["team_number"], "team_nm": t["nickname"]})

        event_["teams_to_keep"].append(t["team_number"])

    insert.append(event_)

    messages = ""
    for e in insert:

        try:
            Event(
                season=season,
                event_nm=e["event_nm"],
                date_st=e["date_st"],
                date_end=e["date_end"],
                event_cd=e["event_cd"],
                event_url=e["event_url"],
                address=e["address"],
                city=e["city"],
                state_prov=e["state_prov"],
                postal_code=e["postal_code"],
                location_name=e["location_name"],
                gmaps_url=e["gmaps_url"],
                webcast_url=e["webcast_url"],
                timezone=e["timezone"],
                current="n",
                competition_page_active="n",
                void_ind="n",
            ).save(force_insert=True)
            messages += "(ADD) Added event: " + e["event_cd"] + "\n"
        except IntegrityError:
            event = Event.objects.get(Q(event_cd=e["event_cd"]) & Q(void_ind="n"))
            event.date_st = e["date_st"]
            event.event_url = e["event_url"]
            event.address = e["address"]
            event.city = e["city"]
            event.state_prov = e["state_prov"]
            event.postal_code = e["postal_code"]
            event.location_name = e["location_name"]
            event.gmaps_url = e["gmaps_url"]
            event.webcast_url = e["webcast_url"]
            event.date_end = e["date_end"]
            event.timezone = e["timezone"]
            event.save()

            messages += "(NO ADD) Already have event: " + e["event_cd"] + "\n"

        # remove teams that have been removed from an event
        event = Event.objects.get(event_cd=e["event_cd"], void_ind="n")
        teams = Team.objects.filter(~Q(team_no__in=e["teams_to_keep"]) & Q(event=event))
        for team in teams:
            team.event_set.remove(event)

        for t in e["teams"]:

            try:
                Team(team_no=t["team_no"], team_nm=t["team_nm"], void_ind="n").save(
                    force_insert=True
                )
                messages += (
                    "(ADD) Added team: " + str(t["team_no"]) + " " + t["team_nm"] + "\n"
                )
            except IntegrityError:
                messages += (
                    "(NO ADD) Already have team: "
                    + str(t["team_no"])
                    + " "
                    + t["team_nm"]
                    + "\n"
                )

            try:  # TODO it doesn't throw an error, but re-linking many to many only keeps one entry in the table for the link
                team = Team.objects.get(team_no=t["team_no"])
                team.event_set.add(
                    Event.objects.get(event_cd=e["event_cd"], void_ind="n")
                )
                messages += (
                    "(LINK) Added team: "
                    + str(t["team_no"])
                    + " "
                    + t["team_nm"]
                    + " to event: "
                    + e["event_cd"]
                    + "\n"
                )
            except IntegrityError:
                messages += (
                    "(NO LINK) Team: "
                    + str(t["team_no"])
                    + " "
                    + t["team_nm"]
                    + " already at event: "
                    + e["event_cd"]
                    + "\n"
                )
    return ret_message(messages)


def sync_matches():
    event = scouting.util.get_current_event()

    insert = []
    messages = ""
    r = requests.get(
        "https://www.thebluealliance.com/api/v3/event/" + event.event_cd + "/matches",
        headers={"X-TBA-Auth-Key": settings.TBA_KEY},
    )
    r = json.loads(r.text)
    match_number = ""
    try:
        for e in r:
            match_number = e.get("match_number", 0)
            red_one = Team.objects.get(
                Q(team_no=e["alliances"]["red"]["team_keys"][0].replace("frc", ""))
                & Q(void_ind="n")
            )
            red_two = Team.objects.get(
                Q(team_no=e["alliances"]["red"]["team_keys"][1].replace("frc", ""))
                & Q(void_ind="n")
            )
            red_three = Team.objects.get(
                Q(team_no=e["alliances"]["red"]["team_keys"][2].replace("frc", ""))
                & Q(void_ind="n")
            )
            blue_one = Team.objects.get(
                Q(team_no=e["alliances"]["blue"]["team_keys"][0].replace("frc", ""))
                & Q(void_ind="n")
            )
            blue_two = Team.objects.get(
                Q(team_no=e["alliances"]["blue"]["team_keys"][1].replace("frc", ""))
                & Q(void_ind="n")
            )
            blue_three = Team.objects.get(
                Q(team_no=e["alliances"]["blue"]["team_keys"][2].replace("frc", ""))
                & Q(void_ind="n")
            )
            red_score = e["alliances"]["red"].get("score", None)
            blue_score = e["alliances"]["blue"].get("score", None)
            comp_level = CompetitionLevel.objects.get(
                Q(comp_lvl_typ=e.get("comp_level", " ")) & Q(void_ind="n")
            )
            time = (
                datetime.datetime.fromtimestamp(
                    e["time"], pytz.timezone("America/New_York")
                )
                if e["time"]
                else None
            )
            match_key = e["key"]

            try:
                match = Match.objects.get(Q(match_id=match_key) & Q(void_ind="n"))

                match.red_one = red_one
                match.red_two = red_two
                match.red_three = red_three
                match.blue_one = blue_one
                match.blue_two = blue_two
                match.blue_three = blue_three
                match.red_score = red_score
                match.blue_score = blue_score
                match.comp_level = comp_level
                match.time = time

                match.save()
                messages += (
                    "(UPDATE) "
                    + event.event_nm
                    + " "
                    + comp_level.comp_lvl_typ_nm
                    + " "
                    + str(match_number)
                    + " "
                    + match_key
                    + "\n"
                )
            except Match.DoesNotExist as odne:
                match = Match(
                    match_id=match_key,
                    match_number=match_number,
                    event=event,
                    red_one=red_one,
                    red_two=red_two,
                    red_three=red_three,
                    blue_one=blue_one,
                    blue_two=blue_two,
                    blue_three=blue_three,
                    red_score=red_score,
                    blue_score=blue_score,
                    comp_level=comp_level,
                    time=time,
                    void_ind="n",
                )
                match.save()
                messages += (
                    "(ADD) "
                    + event.event_nm
                    + " "
                    + comp_level.comp_lvl_typ_nm
                    + " "
                    + str(match_number)
                    + " "
                    + match_key
                    + "\n"
                )
    except:
        messages += "(ERROR) " + event.event_nm + " " + match_number + "\n"
    return messages


def sync_event_team_info(force: int):
    messages = ""
    event = Event.objects.get(current="y")

    now = datetime.datetime.combine(timezone.now(), datetime.time.min)
    date_st = datetime.datetime.combine(event.date_st, datetime.time.min)
    date_end = datetime.datetime.combine(event.date_end, datetime.time.min)

    # Only sync information if the event is active or forcing an update
    if force == 1 or date_st <= now <= date_end:
        r = requests.get(
            "https://www.thebluealliance.com/api/v3/event/"
            + event.event_cd
            + "/rankings",
            headers={"X-TBA-Auth-Key": settings.TBA_KEY},
        )
        r = json.loads(r.text)

        if r is None:
            return "Nothing to sync"

        for e in r.get("rankings", []):
            matches_played = e.get("matches_played", 0)
            qual_average = e.get("qual_average", 0)
            losses = e.get("record", 0).get("losses", 0)
            wins = e.get("record", 0).get("wins", 0)
            ties = e.get("record", 0).get("ties", 0)
            rank = e.get("rank", 0)
            dq = e.get("dq", 0)
            team = Team.objects.get(
                Q(team_no=e["team_key"].replace("frc", "")) & Q(void_ind="n")
            )

            try:
                eti = EventTeamInfo.objects.get(
                    Q(event=event) & Q(team_no=team) & Q(void_ind="n")
                )

                eti.matches_played = matches_played
                eti.qual_average = qual_average
                eti.losses = losses
                eti.wins = wins
                eti.ties = ties
                eti.rank = rank
                eti.dq = dq

                eti.save()
                messages += (
                    "(UPDATE) " + event.event_nm + " " + str(team.team_no) + "\n"
                )
            except EventTeamInfo.DoesNotExist as odne:
                eti = EventTeamInfo(
                    event=event,
                    team_no=team,
                    matches_played=matches_played,
                    qual_average=qual_average,
                    losses=losses,
                    wins=wins,
                    ties=ties,
                    rank=rank,
                    dq=dq,
                )
                eti.save()
                messages += "(ADD) " + event.event_nm + " " + str(team.team_no) + "\n"
    else:
        messages = "No active event"
    return messages


def add_season(year: str):
    try:
        season = Season.objects.get(season=year)
    except Season.DoesNotExist as e:
        season = Season(season=year, current="n").save()

    return season


def save_season(data):
    if data.get("season_id", None) is not None:
        season = Season.objects.get(season_id=data["season_id"])
    else:
        season = Season(season=data["season"], current=data["current"]).save()

    return season


def delete_season(season_id):
    season = Season.objects.get(season_id=season_id)

    events = Event.objects.filter(season=season)
    for e in events:
        delete_event(e.event_id)

    scout_questions = scouting.models.Question.objects.filter(season=season)
    for sq in scout_questions:
        sq.delete()
        sq.question.delete()  # this is the scout question which is an extension model for scouting questions

    season.delete()

    return ret_message("Successfully deleted season: " + season.season)


def save_event(data):
    if (data.get("event_id", None)) is not None:
        event = Event.objects.get(event_id=data["event_id"])
        event.season.season_id = data["season_id"]
        event.event_nm = data["event_nm"]
        event.date_st = data["date_st"]
        event.event_cd = data["event_cd"]
        event.event_url = data.get("event_url", None)
        event.address = data["address"]
        event.city = data["city"]
        event.state_prov = data["state_prov"]
        event.postal_code = data["postal_code"]
        event.location_name = data["location_name"]
        event.gmaps_url = data.get("gmaps_url", None)
        event.webcast_url = data.get("webcast_url", None)
        event.date_end = data["date_end"]
        event.timezone = data["timezone"]
        event.current = data["current"]
        event.competition_page_active = data["competition_page_active"]
        event.void_ind = data["void_ind"]
    else:
        event = Event(
            season_id=data["season_id"],
            event_nm=data["event_nm"],
            date_st=data["date_st"],
            event_cd=data["event_cd"],
            event_url=data.get("event_url", None),
            address=data["address"],
            city=data["city"],
            state_prov=data["state_prov"],
            postal_code=data["postal_code"],
            location_name=data["location_name"],
            gmaps_url=data.get("gmaps_url", None),
            webcast_url=data.get("webcast_url", None),
            date_end=data["date_end"],
            timezone=data["timezone"],
            current=data["current"],
            competition_page_active=data["competition_page_active"],
            void_ind=data["void_ind"],
        )

    event.save()
    return event


def link_team_to_Event(data):
    messages = ""

    for t in data.get("teams", []):
        try:  # TODO it doesn't throw an error, and re-linking many to many only keeps one entry in the table for the link
            if t.get("checked", False):
                team = Team.objects.get(team_no=t["team_no"], void_ind="n")
                e = Event.objects.get(event_id=data["event_id"], void_ind="n")
                team.event_set.add(e)
                messages += (
                    "(ADD) Added team: "
                    + str(t["team_no"])
                    + " "
                    + t["team_nm"]
                    + " to event: "
                    + e.event_cd
                    + "\n"
                )
        except IntegrityError:
            messages += (
                "(NO ADD) Team: "
                + str(t["team_no"])
                + " "
                + t["team_nm"]
                + " already at event: "
                + e.event_cd
                + "\n"
            )

    return messages


def remove_link_team_to_Event(data):
    messages = ""

    for t in data.get("team_no", []):
        try:  # TODO it doesn't throw an error, but re-linking many to many only keeps one entry in the table for the link
            if not t.get("checked", True):
                team = Team.objects.get(team_no=t["team_no"], void_ind="n")
                e = Event.objects.get(event_id=data["event_id"], void_ind="n")
                team.event_set.remove(e)
                messages += (
                    "(REMOVE) Removed team: "
                    + str(t["team_no"])
                    + " "
                    + t["team_nm"]
                    + " from event: "
                    + e.event_cd
                    + "\n"
                )
        except IntegrityError:
            messages += (
                "(NO REMOVE) Team: "
                + str(t["team_no"])
                + " "
                + t["team_nm"]
                + " from event: "
                + e.event_cd
                + "\n"
            )

    return messages


def save_scout_schedule(data):
    if data["end_time"] <= data["st_time"]:
        raise Exception("End time can't come before start.")

    if data.get("scout_field_sch_id", None) is None:
        sfs = ScoutFieldSchedule(
            event_id=data["event_id"],
            st_time=data["st_time"],
            end_time=data["end_time"],
            red_one_id=data.get("red_one_id", None),
            red_two_id=data.get("red_two_id", None),
            red_three_id=data.get("red_three_id", None),
            blue_one_id=data.get("blue_one_id", None),
            blue_two_id=data.get("blue_two_id", None),
            blue_three_id=data.get("blue_three_id", None),
            void_ind=data["void_ind"],
        )
    else:
        sfs = ScoutFieldSchedule.objects.get(
            scout_field_sch_id=data["scout_field_sch_id"]
        )
        sfs.red_one_id = data.get("red_one_id", None)
        sfs.red_two_id = data.get("red_two_id", None)
        sfs.red_three_id = data.get("red_three_id", None)
        sfs.blue_one_id = data.get("blue_one_id", None)
        sfs.blue_two_id = data.get("blue_two_id", None)
        sfs.blue_three_id = data.get("blue_three_id", None)
        sfs.st_time = data["st_time"]
        sfs.end_time = data["end_time"]
        sfs.void_ind = data["void_ind"]

    sfs.save()
    return sfs


def save_schedule(data):
    if data["end_time"] <= data["st_time"]:
        raise Exception("End time can't come before start.")

    if data.get("sch_id", None) is None:
        event = scouting.util.get_current_event()

        s = Schedule(
            event=event,
            st_time=data["st_time"],
            end_time=data["end_time"],
            user_id=data.get("user", None),
            sch_typ_id=data.get("sch_typ", None),
            void_ind=data["void_ind"],
        )
    else:
        s = Schedule.objects.get(sch_id=data["sch_id"])
        s.user = data.get("user", None)
        s.sch_typ_id = data.get("sch_typ", None)
        s.st_time = data["st_time"]
        s.end_time = data["end_time"]
        s.void_ind = data["void_ind"]

    s.save()
    return s


def notify_user(id):
    sch = Schedule.objects.get(sch_id=id)
    message = alerts.util.stage_schedule_alert(sch)
    alerts.util.send_alerts()
    sch.notified = True
    sch.save()

    return message


def notify_users(id):
    event = Event.objects.get(Q(current="y") & Q(void_ind="n"))
    sfs = ScoutFieldSchedule.objects.get(scout_field_sch_id=id)
    message = alerts.util.stage_field_schedule_alerts(-1, [sfs], event)
    alerts.util.send_alerts()
    return message


def get_scouting_user_info():
    user_results = []
    users = user.util.get_users(1, 0)
    for u in users:
        try:
            user_info = u.scouting_user_info.get(void_ind="n")
        except UserInfo.DoesNotExist:
            user_info = {}

        user_results.append(
            {
                "user": u,
                "user_info": user_info,
            }
        )

    return user_results


def toggle_user_under_review(user_id):
    try:
        ui = UserInfo.objects.get(Q(user__id=user_id) & Q(void_ind="n"))
    except UserInfo.DoesNotExist:
        ui = UserInfo(
            user=User.objects.get(id=user_id),
            under_review=False,
        )

    ui.under_review = not ui.under_review

    ui.save()


def get_scout_field_schedule(id):
    return ScoutFieldSchedule.objects.get(scout_field_sch_id=id)


def void_field_response(id):
    sf = ScoutField.objects.get(scout_field_id=id)
    sf.void_ind = "y"
    sf.save()
    return sf


def void_scout_pit_response(id):
    sp = ScoutPit.objects.get(scout_pit_id=id)

    sp.response.void_ind = "y"
    sp.void_ind = "y"
    sp.save()
    return sp
