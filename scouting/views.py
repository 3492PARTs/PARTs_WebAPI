from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response

from general.security import ret_message, access_response
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
    FieldFormFormSerializer,
)
import scouting.util
import scouting.strategizing.util
import scouting.field.util


import time


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
        def fun():
            if request.query_params.get("current", False):
                serializer = SeasonSerializer(scouting.util.get_current_season())
            else:
                serializer = SeasonSerializer(
                    scouting.util.get_all_seasons(), many=True
                )
            return Response(serializer.data)

        return access_response(
            app_url + self.endpoint,
            request.user.id,
            auth_obj,
            "An error occurred while getting seasons.",
            fun,
        )


class EventView(APIView):
    """
    API endpoint to get the list of events
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "event/"

    def get(self, request, format=None):
        def fun():
            events = scouting.util.get_all_events()
            serializer = EventSerializer(events, many=True)
            return Response(serializer.data)

        return access_response(
            app_url + self.endpoint,
            request.user.id,
            auth_obj,
            "An error occurred while getting events.",
            fun,
        )


class TeamView(APIView):
    """
    API endpoint to get the current list of teams
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "team/"

    def get(self, request, format=None):
        def fun():
            teams = scouting.util.get_teams(
                request.query_params.get("current", False) in ["true", True]
            )
            serializer = TeamSerializer(teams, many=True)
            return Response(serializer.data)

        return access_response(
            app_url + self.endpoint,
            request.user.id,
            auth_obj,
            "An error occurred while getting teams.",
            fun,
        )


class MatchView(APIView):
    """
    API endpoint to get the current list of matches
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "match/"

    def get(self, request, format=None):
        def fun():
            matches = scouting.util.get_matches(scouting.util.get_current_event())
            serializer = MatchSerializer(matches, many=True)
            return Response(serializer.data)

        return access_response(
            app_url + self.endpoint,
            request.user.id,
            auth_obj,
            "An error occurred while getting matches.",
            fun,
        )


class ScheduleView(APIView):
    """
    API endpoint to get schedules
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "schedule/"

    def get(self, request, format=None):
        def fun():
            sch = scouting.util.get_current_schedule_parsed()
            serializer = ScheduleSerializer(sch, many=True)
            return Response(serializer.data)

        return access_response(
            app_url + self.endpoint,
            request.user.id,
            auth_obj,
            "An error occurred while getting schedules.",
            fun,
        )


class ScoutFieldScheduleView(APIView):
    """
    API endpoint to get scout field schedules
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "scout-field-schedule/"

    def get(self, request, format=None):
        def fun():
            field_sch = scouting.util.get_current_scout_field_schedule_parsed()
            serializer = ScoutFieldScheduleSerializer(field_sch, many=True)
            return Response(serializer.data)

        return access_response(
            app_url + self.endpoint,
            request.user.id,
            auth_obj,
            "An error occurred while getting scout field schedules.",
            fun,
        )


class ScheduleTypeView(APIView):
    """
    API endpoint to get all schedule types
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "schedule-type/"

    def get(self, request, format=None):
        def fun():
            types = scouting.util.get_schedule_types()
            serializer = ScheduleTypeSerializer(types, many=True)
            return Response(serializer.data)

        return access_response(
            app_url + self.endpoint,
            request.user.id,
            auth_obj,
            "An error occurred while getting schedule types.",
            fun,
        )


class AllScoutingInfo(APIView):
    """
    API endpoint to get the list info needed to populate the scouting app under one call
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "all-scouting-info/"

    def get(self, request, format=None):
        def fun():
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
            team_notes = scouting.strategizing.util.get_team_notes(
                event=current_event
            )
            match_strategies = scouting.strategizing.util.get_match_strategies(
                event=current_event
            )
            field_form_form = scouting.field.util.get_field_form()
            alliance_selections = (
                scouting.strategizing.util.get_alliance_selections()
            )

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
                    "match_strategies": match_strategies,
                    "field_form_form": field_form_form,
                    "alliance_selections": alliance_selections,
                }
            )
            return Response(serializer.data)

        return access_response(
            app_url + self.endpoint,
            request.user.id,
            auth_obj,
            "An error occurred while getting all scouting info.",
            fun,
        )
