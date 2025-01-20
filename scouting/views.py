from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response

from general.security import has_access, ret_message
import scouting
import scouting.models
from scouting.serializers import (
    AllScoutInfoSerializer,
    EventSerializer,
    MatchSerializer,
    ScheduleSerializer,
    ScheduleTypeSerializer,
    ScoutFieldScheduleSerializer,
    SeasonSerializer,
    TeamSerializer,
)
import scouting.util
import scouting.strategizing.util

auth_obj = "scouting"
app_url = "scouting/"


class SeasonView(APIView):
    """
    API endpoint to get the list of seasons
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "season/"

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                seasons = scouting.util.get_all_seasons()

                serializer = SeasonSerializer(seasons, many=True)
                return Response(serializer.data)
            except Exception as e:
                return ret_message(
                    "An error occurred while getting seasons.",
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
    API endpoint to get the list of events
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "event/"

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                events = scouting.util.get_all_events()

                serializer = EventSerializer(events, many=True)
                return Response(serializer.data)
            except Exception as e:
                return ret_message(
                    "An error occurred while getting events.",
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


class TeamView(APIView):
    """
    API endpoint to get the current list of teams
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "team/"

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                teams = scouting.util.get_teams(
                    request.query_params.get("current", False) in ["true", True]
                )

                serializer = TeamSerializer(teams, many=True)
                return Response(serializer.data)
            except Exception as e:
                return ret_message(
                    "An error occurred while getting teams.",
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


class MatchView(APIView):
    """
    API endpoint to get the current list of matches
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "match/"

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                matches = scouting.util.get_matches(scouting.util.get_current_event())
                serializer = MatchSerializer(matches, many=True)
                return Response(serializer.data)
            except Exception as e:
                return ret_message(
                    "An error occurred while getting matches.",
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


class ScheduleView(APIView):
    """
    API endpoint to get schedules
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "schedule/"

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                sch = scouting.util.get_current_schedule_parsed()

                serializer = ScheduleSerializer(sch, many=True)
                return Response(serializer.data)
            except Exception as e:
                return ret_message(
                    "An error occurred while getting schedules.",
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


class ScoutFieldScheduleView(APIView):
    """
    API endpoint to get scout field schedules
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "scout-field-schedule/"

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                field_sch = scouting.util.get_current_scout_field_schedule_parsed()

                serializer = ScoutFieldScheduleSerializer(field_sch, many=True)
                return Response(serializer.data)
            except Exception as e:
                return ret_message(
                    "An error occurred while getting scout field schedules.",
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


class ScheduleTypeView(APIView):
    """
    API endpoint to get all schedule types
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "schedule-type/"

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                types = scouting.util.get_schedule_types()

                serializer = ScheduleTypeSerializer(types, many=True)
                return Response(serializer.data)
            except Exception as e:
                return ret_message(
                    "An error occurred while getting schedule types.",
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


class AllScoutingInfo(APIView):
    """
    API endpoint to get the list info needed to populate the scouting app under one call
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "all-scouting-info/"

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                current_event = scouting.util.get_current_event()

                seasons = scouting.util.get_all_seasons()
                events = scouting.util.get_all_events()
                teams = scouting.util.get_teams(True)
                matches = scouting.util.get_matches(current_event)
                schedules = scouting.util.get_current_schedule_parsed()
                scout_field_schedules = (
                    scouting.util.get_current_scout_field_schedule_parsed()
                )
                schedule_types = scouting.util.get_schedule_types()
                team_notes = scouting.strategizing.util.get_team_notes(event=current_event)
                match_strategies = scouting.strategizing.util.get_match_strategies(event=current_event)

                serializer = AllScoutInfoSerializer(
                    {
                        "seasons": seasons,
                        "events": events,
                        "teams": teams,
                        "matches": matches,
                        "schedules": schedules,
                        "scout_field_schedules": scout_field_schedules,
                        "schedule_types": schedule_types,
                        "team_notes": team_notes,
                        "match_strategies": match_strategies
                    }
                )

                # if not serializer.is_valid():
                #    raise Exception(serializer.errors)

                return Response(serializer.data)
            except Exception as e:
                return ret_message(
                    "An error occurred while getting all scouting info.",
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
