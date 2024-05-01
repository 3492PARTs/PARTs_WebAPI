from ast import Match
import datetime
import json
from django.conf import settings
from django.db import IntegrityError
from django.db.models import Q
import pytz
import requests

from form.models import QuestionAnswer
from general.security import ret_message
from scouting.models import (
    Event,
    EventTeamInfo,
    Schedule,
    ScoutField,
    ScoutFieldSchedule,
    ScoutPit,
    Season,
    Team,
    TeamNotes,
    Match,
)


def load_event(e):
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
    return messages


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
