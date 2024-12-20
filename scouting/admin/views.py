from django.core.exceptions import ObjectDoesNotExist
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated


import scouting.models
import scouting.util
import scouting.admin.util
import scouting.field.util

from .serializers import *
from scouting.models import (
    Season,
    Event,
)
from rest_framework.views import APIView
from general.security import has_access, ret_message
from django.conf import settings
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
        try:
            if has_access(request.user.id, auth_obj):
                groups = scouting.admin.util.get_scout_auth_groups()
                serializer = GroupSerializer(groups, many=True)
                return Response(serializer.data)
            else:
                return ret_message(
                    "You do not have access.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                )
        except Exception as e:
            return ret_message(
                "An error occurred while initializing.",
                True,
                app_url + self.endpoint,
                request.user.id,
                e,
            )


class SyncSeasonView(APIView):
    """
    API endpoint to sync a season
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "sync-season/"

    def get(self, request, format=None):
        try:
            if has_access(request.user.id, auth_obj):
                req = scouting.admin.util.sync_season(
                    request.query_params.get("season_id", None)
                )
                return ret_message(req)
            else:
                return ret_message(
                    "You do not have access.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                )
        except Exception as e:
            return ret_message(
                "An error occurred while syncing the season.",
                True,
                app_url + self.endpoint,
                request.user.id,
                e,
            )


class SyncEventView(APIView):
    """
    API endpoint to sync an event
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "sync-event/"

    def get(self, request, format=None):
        try:
            if has_access(request.user.id, auth_obj):
                return ret_message(
                    scouting.admin.util.sync_event(
                        request.query_params.get("event_cd", None)
                    )
                )
            else:
                return ret_message(
                    "You do not have access.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                )
        except Exception as e:
            return ret_message(
                "An error occurred while syncing the event.",
                True,
                app_url + self.endpoint,
                request.user.id,
                e,
            )


class SyncMatchesView(APIView):
    """
    API endpoint to sync a match
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "sync-matches/"

    def get(self, request, format=None):
        try:
            if has_access(request.user.id, auth_obj):
                req = scouting.admin.util.sync_matches()
                return ret_message(req)
            else:
                return ret_message(
                    "You do not have access.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                )
        except Exception as e:
            return ret_message(
                "An error occurred while syncing matches.",
                True,
                app_url + self.endpoint,
                request.user.id,
                e,
            )


class SyncEventTeamInfoView(APIView):
    """
    API endpoint to sync the info for a teams at an event
    """

    # commented out so the server can call to update
    # authentication_classes = (JWTAuthentication,)
    # permission_classes = (IsAuthenticated,)
    endpoint = "sync-event-team-info/"

    def get(self, request, format=None):
        try:
            req = scouting.admin.util.sync_event_team_info(
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


class SetSeasonEventView(APIView):
    """
    API endpoint to set the season
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "set-season-event/"

    def set(self, season_id, event_id, competition_page_active):
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
            event.competition_page_active = competition_page_active
            event.save()
            msg += "\nSuccessfully set the event to: " + event.event_nm

            msg += f"\nCompetition page {'active' if competition_page_active == 'y' else 'inactive'}"

        return ret_message(msg)

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                req = self.set(
                    request.query_params.get("season_id", None),
                    request.query_params.get("event_id", None),
                    request.query_params.get("competition_page_active", "n"),
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


class SeasonView(APIView):
    """
    API endpoint to add and delete a season
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "season/"

    def post(self, request, format=None):
        try:
            if has_access(request.user.id, auth_obj):
                serializer = SeasonSerializer(data=request.data)
                if not serializer.is_valid():
                    return ret_message(
                        "Invalid data",
                        True,
                        app_url + self.endpoint,
                        request.user.id,
                        serializer.errors,
                    )
                req = scouting.admin.util.add_season(
                    serializer.validated_data["season"]
                )
                return ret_message("Successfully added season: " + req.season)
            else:
                return ret_message(
                    "You do not have access.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                )
        except Exception as e:
            return ret_message(
                "An error occurred while adding the season.",
                True,
                app_url + self.endpoint,
                request.user.id,
                e,
            )

    def put(self, request, format=None):
        try:
            if has_access(request.user.id, auth_obj):
                serializer = SeasonSerializer(data=request.data)
                if not serializer.is_valid():
                    return ret_message(
                        "Invalid data",
                        True,
                        app_url + self.endpoint,
                        request.user.id,
                        serializer.errors,
                    )
                req = scouting.admin.util.save_season(serializer.validated_data)
                ret_message("Successfully saved season")
                return req
            else:
                return ret_message(
                    "You do not have access.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                )
        except Exception as e:
            return ret_message(
                "An error occurred while saving the season.",
                True,
                app_url + self.endpoint,
                request.user.id,
                e,
            )

    def delete(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                req = scouting.admin.util.delete_season(
                    request.query_params.get("season_id", None)
                )
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


class EventView(APIView):
    """
    API endpoint to manage an event
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "add-event/"

    def post(self, request, format=None):
        try:
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
                scouting.admin.util.save_event(serializer.validated_data)
                return ret_message("Successfully added the event.")
            else:
                return ret_message(
                    "You do not have access.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                )
        except Exception as e:
            return ret_message(
                "An error occurred while saving the event.",
                True,
                app_url + self.endpoint,
                request.user.id,
                e,
            )

    def delete(self, request, format=None):
        try:
            if has_access(request.user.id, auth_obj):
                req = scouting.admin.util.delete_event(
                    request.query_params.get("event_id", None)
                )
                return req
            else:
                return ret_message(
                    "You do not have access.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                )
        except Exception as e:
            return ret_message(
                "An error occurred while deleting the event.",
                True,
                app_url + self.endpoint,
                request.user.id,
                e,
            )


class TeamView(APIView):
    """
    API endpoint to add a event
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "team/"

    def post(self, request, format=None):
        try:
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
                serializer.save()
                return ret_message("Successfully added the team.")
            else:
                return ret_message(
                    "You do not have access.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                )
        except Exception as e:
            return ret_message(
                "An error occurred while saving the team.",
                True,
                app_url + self.endpoint,
                request.user.id,
                e,
            )


class TeamToEventView(APIView):
    """
    API endpoint to add a team to an event
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "team-to-event/"

    def post(self, request, format=None):
        try:
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
                req = scouting.admin.util.link_team_to_Event(serializer.validated_data)
                return ret_message(req)
            else:
                return ret_message(
                    "You do not have access.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                )
        except Exception as e:
            return ret_message(
                "An error occurred while saving the team.",
                True,
                app_url + self.endpoint,
                request.user.id,
                e,
            )


class RemoveTeamToEventView(APIView):
    """
    API endpoint to remove a team from an event
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "remove-team-to-event/"

    def post(self, request, format=None):
        try:
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
                req = scouting.admin.util.remove_link_team_to_Event(
                    serializer.validated_data
                )
                return ret_message(req)
            else:
                return ret_message(
                    "You do not have access.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                )
        except Exception as e:
            return ret_message(
                "An error occurred while removing the team.",
                True,
                app_url + self.endpoint,
                request.user.id,
                e,
            )


class ScoutFieldScheduleView(APIView):
    """API endpoint to save scout schedule entry"""

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "scout-field-schedule-entry/"

    def post(self, request, format=None):
        try:
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
                scouting.admin.util.save_scout_schedule(serializer.validated_data)
                return ret_message("Saved field schedule entry.")
            else:
                return ret_message(
                    "You do not have access.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                )
        except Exception as e:
            return ret_message(
                "An error occurred while saving the field schedule entry.",
                True,
                app_url + self.endpoint,
                request.user.id,
                e,
            )


class ScheduleView(APIView):
    """API endpoint to save a schedule entry"""

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "schedule-entry/"

    def post(self, request, format=None):
        try:
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
                scouting.admin.util.save_schedule(serializer.validated_data)
                return ret_message("Saved schedule entry.")
            else:
                return ret_message(
                    "You do not have access.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                )
        except Exception as e:
            return ret_message(
                "An error occurred while saving the schedule entry.",
                True,
                app_url + self.endpoint,
                request.user.id,
                e,
            )


class NotifyUserView(APIView):
    """API endpoint to notify users"""

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "notify-user/"

    def get(self, request, format=None):
        try:
            if has_access(request.user.id, auth_obj):
                scout_field_sch_id = request.query_params.get(
                    "scout_field_sch_id", None
                )
                sch_id = request.query_params.get("sch_id", None)
                if scout_field_sch_id is not None:
                    req = scouting.admin.util.notify_users(scout_field_sch_id)
                elif sch_id is not None:
                    req = scouting.admin.util.notify_user(sch_id)
                else:
                    raise Exception("No ID provided.")
                return ret_message(req)
            else:
                return ret_message(
                    "You do not have access.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                )
        except Exception as e:
            return ret_message(
                "An error occurred while notifying the user.",
                True,
                app_url + self.endpoint,
                request.user.id,
                e,
            )


class ScoutingUserInfoView(APIView):
    """
    API endpoint to get scouters user info
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "scouting-user-info/"

    def get(self, request, format=None):
        try:
            if has_access(request.user.id, auth_obj):
                req = scouting.admin.util.get_scouting_user_info()
                serializer = UserScoutingUserInfoSerializer(req, many=True)
                return Response(serializer.data)
            else:
                return ret_message(
                    "You do not have access.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                )
        except Exception as e:
            return ret_message(
                "An error occurred while getting scouting activity.",
                True,
                app_url + self.endpoint,
                request.user.id,
                e,
            )


class ToggleScoutUnderReviewView(APIView):
    """
    API endpoint to toggle a scout under review status
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "toggle-scout-under-review/"

    def get(self, request, format=None):
        try:
            if has_access(request.user.id, auth_obj):
                scouting.admin.util.toggle_user_under_review(
                    request.query_params.get("user_id", None)
                )
                return ret_message("Successfully changed scout under review status")
            else:
                return ret_message(
                    "You do not have access.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                )
        except Exception as e:
            return ret_message(
                "An error occurred while changing the scout" "s under review status.",
                True,
                app_url + self.endpoint,
                request.user.id,
                e,
            )


class MarkScoutPresentView(APIView):
    """
    API endpoint to mark a scout present for their shift
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "mark-scout-present/"

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                sfs = scouting.util.get_scout_field_schedule(
                    request.query_params.get("scout_field_sch_id", None)
                )
                user_id = int(request.query_params.get("user_id", None))
                return ret_message(scouting.field.util.check_in_scout(sfs, user_id))
            except Exception as e:
                return ret_message(
                    "An error occurred while marking the scout" " present.",
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


class FieldResponseView(APIView):
    """
    API endpoint to delete a field scouting result
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "delete-field-result/"

    def delete(self, request, format=None):
        try:
            if has_access(request.user.id, auth_obj):
                scouting.admin.util.void_field_response(
                    request.query_params["scout_field_id"]
                )
                return ret_message("Successfully deleted result")
            else:
                return ret_message(
                    "You do not have access.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                )
        except Exception as e:
            return ret_message(
                "An error occurred while deleting result.",
                True,
                app_url + self.endpoint,
                request.user.id,
                e,
            )


class PitResponseView(APIView):
    """
    API endpoint to delete a pit scouting result
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "delete-pit-result/"

    def delete(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                scouting.admin.util.void_scout_pit_response(
                    request.query_params["scout_pit_id"]
                )
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
