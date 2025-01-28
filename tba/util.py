import requests
import datetime
import json
from hashlib import sha256
import hmac
from django.conf import settings
from django.db import IntegrityError
from django.db.models import Q
import pytz
from django.utils import timezone

import scouting
from scouting.models import (
    CompetitionLevel,
    Event,
    EventTeamInfo,
    Season,
    Team,
    Match,
)
import scouting.util
import scouting.models
from tba.models import Message

tba_url = "https://www.thebluealliance.com/api/v3"


def sync_season(season_id):
    season = Season.objects.get(season_id=season_id)

    request = requests.get(
        f"{tba_url}/team/frc3492/events/{season.season}",
        headers={"X-TBA-Auth-Key": settings.TBA_KEY},
    )
    request = json.loads(request.text)

    messages = ""
    for event in request:
        messages += sync_event(event["key"])
        messages += "------------------------------------------------\n"

    return messages


def sync_event(event_cd: str):
    request = requests.get(
        f"{tba_url}/event/{event_cd}",
        headers={"X-TBA-Auth-Key": settings.TBA_KEY},
    )
    tba_event = json.loads(request.text)

    if tba_event.get("Error", None) is not None:
        raise Exception(tba_event["Error"])

    season = Season.objects.get(season=tba_event["year"])
    time_zone = (
        tba_event.get("timezone")
        if tba_event.get("timezone", None) is not None
        else "America/New_York"
    )

    event_ = {
        "event_nm": tba_event["name"],
        "date_st": datetime.datetime.strptime(
            tba_event["start_date"], "%Y-%m-%d"
        ).astimezone(pytz.timezone(time_zone)),
        "date_end": datetime.datetime.strptime(
            tba_event["end_date"], "%Y-%m-%d"
        ).astimezone(pytz.timezone(time_zone)),
        "event_cd": tba_event["key"],
        "event_url": tba_event.get("event_url", None),
        "gmaps_url": tba_event.get("gmaps_url", None),
        "address": tba_event.get("address", None),
        "city": tba_event.get("city", None),
        "state_prov": tba_event.get("state_prov", None),
        "postal_code": tba_event.get("postal_code", None),
        "location_name": tba_event.get("location_name", None),
        "timezone": tba_event.get("timezone", "America/New_York"),
        "webcast_url": (
            tba_event["webcasts"][0]["channel"]
            if len(tba_event["webcasts"]) > 0
            else ""
        ),
        "teams": [],
        "teams_to_keep": [],
    }

    request = requests.get(
        f"{tba_url}/event/{tba_event['key']}/teams",
        headers={"X-TBA-Auth-Key": settings.TBA_KEY},
    )
    tba_teams = json.loads(request.text)

    for t in tba_teams:
        event_["teams"].append({"team_no": t["team_number"], "team_nm": t["nickname"]})

        event_["teams_to_keep"].append(t["team_number"])

    messages = ""
    try:
        event = Event.objects.get(event_cd=event_["event_cd"])
        event.void_ind = "n"
        event.date_st = event_["date_st"]
        event.date_end = event_["date_end"]

        messages += "(NO ADD) Already have event: " + event_["event_cd"] + "\n"
    except Event.DoesNotExist as e:
        event = Event(
            season=season,
            event_cd=event_["event_cd"],
            date_st=event_["date_st"],
            date_end=event_["date_end"],
            current="n",
            competition_page_active="n",
            void_ind="n",
        )

        event.save(force_insert=True)
        messages += "(ADD) Added event: " + event_["event_cd"] + "\n"

    event.event_nm = event_["event_nm"]
    event.event_url = event_["event_url"]
    event.address = event_["address"]
    event.city = event_["city"]
    event.state_prov = event_["state_prov"]
    event.postal_code = event_["postal_code"]
    event.location_name = event_["location_name"]
    event.gmaps_url = event_["gmaps_url"]
    event.webcast_url = event_["webcast_url"]
    event.timezone = event_["timezone"]
    event.save()

    # remove teams that have been removed from an event
    teams = Team.objects.filter(
        ~Q(team_no__in=event_["teams_to_keep"]) & Q(event=event)
    )
    for team in teams:
        team.event_set.remove(event)
        messages += f"(REMOVE) Removed team: {team['team_no']} {team['team_nm']} from event: {event_['event_cd']}\n"

    for team_ in event_["teams"]:
        try:
            team = Team(
                team_no=team_["team_no"], team_nm=team_["team_nm"], void_ind="n"
            )
            team.save(force_insert=True)
            messages += f"(ADD) Added team: {team_['team_no']} {team_['team_nm']}\n"
        except IntegrityError:
            team = Team.objects.get(team_no=team_["team_no"])
            messages += (
                f"(NO ADD) Already have team: {team_['team_no']} {team_['team_nm']}\n"
            )

        try:  # TODO it doesn't throw an error, but re-linking many to many only keeps one entry in the table for the link
            team.event_set.add(event)
            messages += f"(LINK) Added team: {team_['team_no']} {team_['team_nm']} to event: {event_['event_cd']}\n"
        except IntegrityError:
            messages += f"(NO LINK) Team: {team_['team_no']} {team_['team_nm']} already at event: {event_['event_cd']}\n"

    return messages


def sync_matches():
    event = scouting.util.get_current_event()

    messages = ""
    request = requests.get(
        f"{tba_url}/event/{event.event_cd}/matches",
        headers={"X-TBA-Auth-Key": settings.TBA_KEY},
    )
    matches = json.loads(request.text)
    match_number = ""
    try:
        for match in matches:
            match_number = match.get("match_number", 0)
            messages += save_tba_match(event, match)
    except Exception as e:
        messages += f"(ERROR) {event.event_nm} {match_number} {e}\n"
    return messages


def sync_event_team_info(force: int):
    messages = ""
    event = Event.objects.get(current="y")

    sync_event(event.event_cd)

    now = datetime.datetime.combine(timezone.now(), datetime.time.min)
    date_st = datetime.datetime.combine(event.date_st, datetime.time.min)
    date_end = datetime.datetime.combine(event.date_end, datetime.time.min)

    # Only sync information if the event is active or forcing an update
    if force == 1 or date_st <= now <= date_end:
        request = requests.get(
            f"{tba_url}/event/{event.event_cd}/rankings",
            headers={"X-TBA-Auth-Key": settings.TBA_KEY},
        )
        rankings = json.loads(request.text)

        if rankings is None:
            return "Nothing to sync"

        for info in rankings.get("rankings", []):
            matches_played = info.get("matches_played", 0)
            qual_average = info.get("qual_average", 0)
            losses = (
                info["record"].get("losses", 0) if info.get("record", 0) is not None else 0
            )
            wins = info["record"].get("wins", 0) if info.get("record", 0) is not None else 0
            ties = info["record"].get("ties", 0) if info.get("record", 0) is not None else 0
            rank = info.get("rank", 0)
            dq = info.get("dq", 0)
            team = Team.objects.get(
                Q(team_no=info["team_key"].replace("frc", "")) & Q(void_ind="n")
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
                messages += f"(UPDATE) {event.event_nm} {team.team}\n"
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
                messages += f"(ADD) {event.event_nm} {team.team}\n"
    else:
        messages = "No active event"
    return messages


def save_tba_match(tba_match):
    event = Event.objects.get(event_cd=tba_match["event_key"])
    messages = ""
    match_number = tba_match.get("match_number", 0)
    red_one = Team.objects.get(
        Q(team_no=tba_match["alliances"]["red"]["team_keys"][0].replace("frc", ""))
        & Q(void_ind="n")
    )
    red_two = Team.objects.get(
        Q(team_no=tba_match["alliances"]["red"]["team_keys"][1].replace("frc", ""))
        & Q(void_ind="n")
    )
    red_three = Team.objects.get(
        Q(team_no=tba_match["alliances"]["red"]["team_keys"][2].replace("frc", ""))
        & Q(void_ind="n")
    )
    blue_one = Team.objects.get(
        Q(team_no=tba_match["alliances"]["blue"]["team_keys"][0].replace("frc", ""))
        & Q(void_ind="n")
    )
    blue_two = Team.objects.get(
        Q(team_no=tba_match["alliances"]["blue"]["team_keys"][1].replace("frc", ""))
        & Q(void_ind="n")
    )
    blue_three = Team.objects.get(
        Q(team_no=tba_match["alliances"]["blue"]["team_keys"][2].replace("frc", ""))
        & Q(void_ind="n")
    )
    red_score = tba_match["alliances"]["red"].get("score", None)
    blue_score = tba_match["alliances"]["blue"].get("score", None)
    comp_level = CompetitionLevel.objects.get(
        Q(comp_lvl_typ=tba_match.get("comp_level", " ")) & Q(void_ind="n")
    )
    time = (
        datetime.datetime.fromtimestamp(
            tba_match["time"], pytz.timezone("America/New_York")
        )
        if tba_match["time"]
        else None
    )
    match_key = tba_match["key"]

    try:
        match = Match.objects.get(Q(match_id=match_key))

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
        match.void_ind = "n"

        match.save()
        messages += f"(UPDATE) {event.event_nm} {comp_level.comp_lvl_typ_nm} {match_number} {match_key}\n"
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
        messages += f"(ADD) {event.event_nm} {comp_level.comp_lvl_typ_nm} {match_number} {match_key}\n"

    return  messages


def save_message(message):
    msg = Message(message_type=message["message_type"], message_data=message["message_data"])
    msg.save()
    return msg

def verify_tba_webhook_call(request):
    json_str = json.dumps(request.data, ensure_ascii=True)
    hmac_hex = hmac.new(
        settings.TBA_WEBHOOK_SECRET.encode("utf-8"), json_str.encode("utf-8"), sha256
    ).hexdigest()
    return hmac_hex == request.META.get("HTTP_X_TBA_HMAC", None)