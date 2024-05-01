import datetime
import pytz
from django.db import IntegrityError, transaction
from django.core.exceptions import ObjectDoesNotExist
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.utils import json
from django.utils import timezone

import alerts.util
import scouting.models
import scouting.util
import scouting.admin.util
import user.util
from form.models import Question, QuestionAnswer, FormType
from user.models import User, PhoneType

from .serializers import *
from scouting.models import (
    Schedule,
    Season,
    Event,
    ScoutAuthGroups,
    ScoutFieldSchedule,
    Team,
    CompetitionLevel,
    Match,
    EventTeamInfo,
    ScoutField,
    ScoutPit,
    TeamNotes,
    UserInfo,
)
from rest_framework.views import APIView
from general.security import has_access, ret_message
import requests
from django.conf import settings
from django.db.models.functions import Lower
from django.db.models import Q
from rest_framework.response import Response

auth_obj = "scoutadmin"
app_url = "scouting/admin/"


class ScoutAuthGroupsView(APIView):
    """
    API endpoint to get auth groups available to the scouting admin screen
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "scout-auth-group/"

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                sags = ScoutAuthGroups.objects.all().order_by("auth_group_id__name")

                groups = []

                for sag in sags:
                    groups.append(sag.auth_group_id)

                serializer = GroupSerializer(groups, many=True)
                return Response(serializer.data)
            except Exception as e:
                return ret_message(
                    "An error occurred while initializing.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                    e,
                )
        else:
            return ret_message(
                "You do not have access.",
                True,
                app_url + self.endpoint,
                request.user.id,
            )


class SyncSeason(APIView):
    """
    API endpoint to sync a season
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "sync-season/"

    def sync_season(self, season_id):
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

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                req = self.sync_season(request.query_params.get("season_id", None))
                return ret_message(req)
            except Exception as e:
                return ret_message(
                    "An error occurred while syncing the season/event/teams.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                    e,
                )
        else:
            return ret_message(
                "You do not have access.",
                True,
                app_url + self.endpoint,
                request.user.id,
            )


class SyncEvent(APIView):
    """
    API endpoint to sync an event
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "sync-event/"

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                r = requests.get(
                    "https://www.thebluealliance.com/api/v3/event/"
                    + request.query_params.get("event_cd", None),
                    headers={"X-TBA-Auth-Key": settings.TBA_KEY},
                )
                r = json.loads(r.text)

                if r.get("Error", None) is not None:
                    return ret_message(
                        r["Error"], True, app_url + self.endpoint, request.user.id
                    )
                return ret_message(scouting.admin.util.load_event(r))
            except Exception as e:
                return ret_message(
                    "An error occurred while syncing the season/event/teams.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                    e,
                )
        else:
            return ret_message(
                "You do not have access.",
                True,
                app_url + self.endpoint,
                request.user.id,
            )


class SyncMatches(APIView):
    """
    API endpoint to sync a season
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "sync-matches/"

    def sync_matches(self):
        event = Event.objects.get(current="y")

        insert = []
        messages = ""
        r = requests.get(
            "https://www.thebluealliance.com/api/v3/event/"
            + event.event_cd
            + "/matches",
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
                except ObjectDoesNotExist as odne:
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
            messages += "(EROR) " + event.event_nm + " " + match_number + "\n"
        return messages

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                req = self.sync_matches()
                return ret_message(req)
            except Exception as e:
                return ret_message(
                    "An error occurred while syncing matches.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                    e,
                )
        else:
            return ret_message(
                "You do not have access.",
                True,
                app_url + self.endpoint,
                request.user.id,
            )


class SyncEventTeamInfo(APIView):
    """
    API endpoint to sync the info for a teams at an event
    """

    # commented out so the server can call to update
    # authentication_classes = (JWTAuthentication,)
    # permission_classes = (IsAuthenticated,)
    endpoint = "sync-event-team-info/"

    def sync_event_team_info(self, force: int):
        messages = ""
        event = Event.objects.get(current="y")

        now = datetime.datetime.combine(timezone.now(), datetime.time.min)
        date_st = datetime.datetime.combine(event.date_st, datetime.time.min)
        date_end = datetime.datetime.combine(event.date_end, datetime.time.min)
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
                except ObjectDoesNotExist as odne:
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
                    messages += (
                        "(ADD) " + event.event_nm + " " + str(team.team_no) + "\n"
                    )
        else:
            messages = "No active event"
        return messages

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                req = self.sync_event_team_info(
                    int(request.query_params.get("force", "0"))
                )
                return ret_message(req)
            except Exception as e:
                return ret_message(
                    "An error occurred while syncing event team info.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                    e,
                )
        else:
            return ret_message(
                "You do not have access.",
                True,
                app_url + self.endpoint,
                request.user.id,
            )


class SetSeason(APIView):
    """
    API endpoint to set the season
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "set-season/"

    def set(self, season_id, event_id):
        msg = ""

        Season.objects.filter(current="y").update(current="n")
        season = Season.objects.get(season_id=season_id)
        season.current = "y"
        season.save()
        msg = "Successfully set the season to: " + season.season

        if event_id is not None:
            Event.objects.filter(current="y").update(
                current="n", competition_page_active="n"
            )
            event = Event.objects.get(event_id=event_id)
            event.current = "y"
            event.save()
            msg += "\nSuccessfully set the event to: " + event.event_nm

        return ret_message(msg)

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                req = self.set(
                    request.query_params.get("season_id", None),
                    request.query_params.get("event_id", None),
                )
                return req
            except Exception as e:
                return ret_message(
                    "An error occurred while setting the season.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                    e,
                )
        else:
            return ret_message(
                "You do not have access.",
                True,
                app_url + self.endpoint,
                request.user.id,
            )


class ToggleCompetitionPage(APIView):
    """
    API endpoint to toggle a scout field question
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "toggle-competition-page/"

    def toggle(self, sq_id):
        try:
            event = Event.objects.get(Q(current="y") & Q(void_ind="n"))

            if event.competition_page_active == "n":
                event.competition_page_active = "y"
            else:
                event.competition_page_active = "n"
            event.save()
        except ObjectDoesNotExist as odne:
            return ret_message(
                "No active event, can't activate competition page",
                True,
                app_url + self.endpoint,
                self.request.user.id,
                odne,
            )

        return ret_message("Successfully toggled competition page.")

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                req = self.toggle(request.query_params.get("sq_id", None))
                return req
            except Exception as e:
                return ret_message(
                    "An error occurred while toggling the competition page.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                    e,
                )
        else:
            return ret_message(
                "You do not have access.",
                True,
                app_url + self.endpoint,
                request.user.id,
            )


class AddSeason(APIView):
    """
    API endpoint to add a season
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "add-season/"

    def add(self, season):
        try:
            Season.objects.get(season=season)
            return ret_message(
                "Season not added. Season " + season + " already exists.",
                True,
                app_url + self.endpoint,
                self.request.user.id,
            )
        except Exception as e:
            Season(season=season, current="n").save()

        return ret_message("Successfully added season: " + season)

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                req = self.add(request.query_params.get("season", None))
                return req
            except Exception as e:
                return ret_message(
                    "An error occurred while setting the season.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                    e,
                )
        else:
            return ret_message(
                "You do not have access.",
                True,
                app_url + self.endpoint,
                request.user.id,
            )


class AddEvent(APIView):
    """
    API endpoint to add a event
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "add-event/"

    def post(self, request, format=None):
        serializer = EventSerializer(data=request.data)
        if not serializer.is_valid():
            return ret_message(
                "Invalid data",
                True,
                app_url + self.endpoint,
                request.user.id,
                serializer.errors,
            )

        if has_access(request.user.id, auth_obj):
            try:
                serializer.save()
                return ret_message("Successfully added the event.")
            except Exception as e:
                return ret_message(
                    "An error occurred while saving the event.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                    e,
                )
        else:
            return ret_message(
                "You do not have access.",
                True,
                app_url + self.endpoint,
                request.user.id,
            )


class DeleteEvent(APIView):
    """
    API endpoint to delete an event
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "delete-event/"

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                req = scouting.admin.util.delete_event(
                    request.query_params.get("event_id", None)
                )
                return req
            except Exception as e:
                return ret_message(
                    "An error occurred while deleting the event.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                    e,
                )
        else:
            return ret_message(
                "You do not have access.",
                True,
                app_url + self.endpoint,
                request.user.id,
            )


class AddTeam(APIView):
    """
    API endpoint to add a event
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "add-team/"

    def post(self, request, format=None):
        serializer = TeamCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return ret_message(
                "Invalid data",
                True,
                app_url + self.endpoint,
                request.user.id,
                serializer.errors,
            )

        if has_access(request.user.id, auth_obj):
            try:
                serializer.save()
                return ret_message("Successfully added the team.")
            except Exception as e:
                return ret_message(
                    "An error occurred while saving the team.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                    e,
                )
        else:
            return ret_message(
                "You do not have access.",
                True,
                app_url + self.endpoint,
                request.user.id,
            )


class AddTeamToEvent(APIView):
    """
    API endpoint to add a team to an event
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "add-team-to-event/"

    def link(self, data):
        messages = ""

        for t in data.get("teams", []):
            try:  # TODO it doesn't throw an error, but re-linking many to many only keeps one entry in the table for the link
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

    def post(self, request, format=None):
        serializer = EventToTeamsSerializer(data=request.data)
        if not serializer.is_valid():
            return ret_message(
                "Invalid data",
                True,
                app_url + self.endpoint,
                request.user.id,
                serializer.errors,
            )

        if has_access(request.user.id, auth_obj):
            try:
                req = self.link(serializer.validated_data)
                return ret_message(req)
            except Exception as e:
                return ret_message(
                    "An error occurred while saving the team.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                    e,
                )
        else:
            return ret_message(
                "You do not have access.",
                True,
                app_url + self.endpoint,
                request.user.id,
            )


class RemoveTeamToEvent(APIView):
    """
    API endpoint to remove a team from an event
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "remove-team-to-event/"

    def link(self, data):
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

    def post(self, request, format=None):
        serializer = EventTeamSerializer(data=request.data)
        if not serializer.is_valid():
            return ret_message(
                "Invalid data",
                True,
                app_url + self.endpoint,
                request.user.id,
                serializer.errors,
            )

        if has_access(request.user.id, auth_obj):
            try:
                req = self.link(serializer.validated_data)
                return ret_message(req)
            except Exception as e:
                return ret_message(
                    "An error occurred while removing the team.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                    e,
                )
        else:
            return ret_message(
                "You do not have access.",
                True,
                app_url + self.endpoint,
                request.user.id,
            )


class DeleteSeason(APIView):
    """
    API endpoint to delete a season
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "delete-season/"

    def delete(self, season_id):
        season = Season.objects.get(season_id=season_id)

        events = Event.objects.filter(season=season)
        for e in events:
            scouting.admin.util.delete_event(e.event_id)

        scout_questions = scouting.models.Question.objects.filter(season=season)
        for sq in scout_questions:
            sq.delete()
            questions = Question.objects.filter(question=sq.question)
            for q in questions:
                q.delete()

        season.delete()

        return ret_message("Successfully deleted season: " + season.season)

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                req = self.delete(request.query_params.get("season_id", None))
                return req
            except Exception as e:
                return ret_message(
                    "An error occurred while deleting the season.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                    e,
                )
        else:
            return ret_message(
                "You do not have access.",
                True,
                app_url + self.endpoint,
                request.user.id,
            )


class SaveScoutFieldScheduleEntry(APIView):
    """API endpoint to save scout schedule entry"""

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "save-scout-field-schedule-entry/"

    def save_scout_schedule(self, serializer):
        """
        if serializer.validated_data['st_time'] <= timezone.now():
            return ret_message('Start time can\'t be in the past.', True, app_url + self.endpoint,
                               self.request.user.id)
        """

        if (
            serializer.validated_data["end_time"]
            <= serializer.validated_data["st_time"]
        ):
            return ret_message(
                "End time can't come before start.",
                True,
                app_url + self.endpoint,
                self.request.user.id,
            )

        if serializer.validated_data.get("scout_field_sch_id", None) is None:
            serializer.save()
            return ret_message("Saved schedule entry successfully")
        else:
            sfs = ScoutFieldSchedule.objects.get(
                scout_field_sch_id=serializer.validated_data["scout_field_sch_id"]
            )
            sfs.red_one_id = serializer.validated_data.get("red_one_id", None)
            sfs.red_two_id = serializer.validated_data.get("red_two_id", None)
            sfs.red_three_id = serializer.validated_data.get("red_three_id", None)
            sfs.blue_one_id = serializer.validated_data.get("blue_one_id", None)
            sfs.blue_two_id = serializer.validated_data.get("blue_two_id", None)
            sfs.blue_three_id = serializer.validated_data.get("blue_three_id", None)
            sfs.st_time = serializer.validated_data["st_time"]
            sfs.end_time = serializer.validated_data["end_time"]
            sfs.void_ind = serializer.validated_data["void_ind"]
            sfs.save()
            return ret_message("Updated schedule entry successfully")

    def post(self, request, format=None):
        serializer = ScoutFieldScheduleSaveSerializer(data=request.data)
        if not serializer.is_valid():
            return ret_message(
                "Invalid data",
                True,
                app_url + self.endpoint,
                request.user.id,
                serializer.errors,
            )

        if has_access(request.user.id, auth_obj):
            try:
                req = self.save_scout_schedule(serializer)
                return req
            except Exception as e:
                return ret_message(
                    "An error occurred while saving the schedule entry.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                    e,
                )
        else:
            return ret_message(
                "You do not have access.",
                True,
                app_url + self.endpoint,
                request.user.id,
            )


class SaveScheduleEntry(APIView):
    """API endpoint to save a schedule entry"""

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "save-schedule-entry/"

    def save_schedule(self, serializer):
        """
        if serializer.validated_data['st_time'] <= timezone.now():
            return ret_message('Start time can\'t be in the past.', True, app_url + self.endpoint,
                               self.request.user.id)
        """

        if (
            serializer.validated_data["end_time"]
            <= serializer.validated_data["st_time"]
        ):
            return ret_message(
                "End time can't come before start.",
                True,
                app_url + self.endpoint,
                self.request.user.id,
            )

        if serializer.validated_data.get("sch_id", None) is None:
            serializer.save()
            return ret_message("Saved schedule entry successfully")
        else:
            s = Schedule.objects.get(sch_id=serializer.validated_data["sch_id"])
            s.user_id = serializer.validated_data.get("user", None)
            s.sch_typ_id = serializer.validated_data.get("sch_typ", None)
            s.st_time = serializer.validated_data["st_time"]
            s.end_time = serializer.validated_data["end_time"]
            s.void_ind = serializer.validated_data["void_ind"]
            s.save()
            return ret_message("Updated schedule entry successfully")

    def post(self, request, format=None):
        serializer = ScheduleSaveSerializer(data=request.data)
        if not serializer.is_valid():
            return ret_message(
                "Invalid data",
                True,
                app_url + self.endpoint,
                request.user.id,
                serializer.errors,
            )

        if has_access(request.user.id, auth_obj):
            try:
                req = self.save_schedule(serializer)
                return req
            except Exception as e:
                return ret_message(
                    "An error occurred while saving the schedule entry.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                    e,
                )
        else:
            return ret_message(
                "You do not have access.",
                True,
                app_url + self.endpoint,
                request.user.id,
            )


class NotifyUser(APIView):
    """API endpoint to notify users"""

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "notify-user/"

    def notify_user(self, id):
        sch = Schedule.objects.get(sch_id=id)
        message = alerts.util.stage_schedule_alert(sch)
        alerts.util.send_alerts()
        sch.notified = True
        sch.save()

        return ret_message(message)

    def notify_users(self, id):
        event = Event.objects.get(Q(current="y") & Q(void_ind="n"))
        sfs = ScoutFieldSchedule.objects.get(scout_field_sch_id=id)
        message = alerts.util.stage_field_schedule_alerts(-1, [sfs], event)
        alerts.util.send_alerts()
        return ret_message(message)

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                with transaction.atomic():
                    scout_field_sch_id = request.query_params.get(
                        "scout_field_sch_id", None
                    )
                    sch_id = request.query_params.get("sch_id", None)
                    if scout_field_sch_id is not None:
                        req = self.notify_users(scout_field_sch_id)
                    elif sch_id is not None:
                        req = self.notify_user(sch_id)
                    else:
                        raise Exception("No ID provided.")
                    return req
            except Exception as e:
                return ret_message(
                    "An error occurred while notifying the user.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                    e,
                )
        else:
            return ret_message(
                "You do not have access.",
                True,
                app_url + self.endpoint,
                request.user.id,
            )


class ScoutingUserInfo(APIView):
    """
    API endpoint to get scouters user info
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "scouting-user-info/"

    def init(self):
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

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                req = self.init()
                serializer = UserScoutingUserInfoSerializer(req, many=True)
                return Response(serializer.data)
            except Exception as e:
                return ret_message(
                    "An error occurred while getting scouting activity.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                    e,
                )
        else:
            return ret_message(
                "You do not have access.",
                True,
                app_url + self.endpoint,
                request.user.id,
            )


class ToggleScoutUnderReview(APIView):
    """
    API endpoint to toggle a scout under review status
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "toggle-scout-under-review/"

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                try:
                    ui = UserInfo.objects.get(
                        Q(user__id=request.query_params.get("user_id", None))
                        & Q(void_ind="n")
                    )
                except UserInfo.DoesNotExist:
                    ui = UserInfo(
                        user=User.objects.get(
                            id=request.query_params.get("user_id", None)
                        ),
                        under_review=False,
                    )

                ui.under_review = not ui.under_review

                ui.save()

                return ret_message("Successfully changed scout under review status")
            except Exception as e:
                return ret_message(
                    "An error occurred while changing the scout"
                    "s under review status.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                    e,
                )
        else:
            return ret_message(
                "You do not have access.",
                True,
                app_url + self.endpoint,
                request.user.id,
            )


class MarkScoutPresent(APIView):
    """
    API endpoint to mark a scout present for their shift
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "mark-scout-present/"

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                sfs = ScoutFieldSchedule.objects.get(
                    scout_field_sch_id=request.query_params.get(
                        "scout_field_sch_id", None
                    )
                )
                user_id = int(request.query_params.get("user_id", None))
                return ret_message(scouting.field.views.check_in_scout(sfs, user_id))
            except Exception as e:
                return ret_message(
                    "An error occurred while changing the scout"
                    "s under review status.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                    e,
                )
        else:
            return ret_message(
                "You do not have access.",
                True,
                app_url + self.endpoint,
                request.user.id,
            )


class DeleteFieldResult(APIView):
    """
    API endpoint to delete a field scouting result
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "delete-field-result/"

    def delete(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                sf = ScoutField.objects.get(
                    scout_field_id=request.query_params["scout_field_id"]
                )
                sf.void_ind = "y"
                sf.save()

                return ret_message("Successfully deleted result")
            except Exception as e:
                return ret_message(
                    "An error occurred while deleting result.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                    e,
                )
        else:
            return ret_message(
                "You do not have access.",
                True,
                app_url + self.endpoint,
                request.user.id,
            )


class DeletePitResult(APIView):
    """
    API endpoint to delete a pit scouting result
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "delete-pit-result/"

    def delete(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                sp = ScoutPit.objects.get(
                    scout_pit_id=request.query_params["scout_pit_id"]
                )

                sp.response.void_ind = "y"
                sp.void_ind = "y"
                sp.save()

                return ret_message("Successfully deleted result")
            except Exception as e:
                return ret_message(
                    "An error occurred while deleting result.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                    e,
                )
        else:
            return ret_message(
                "You do not have access.",
                True,
                app_url + self.endpoint,
                request.user.id,
            )
