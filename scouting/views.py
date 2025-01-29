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
    TeamSerializer, FieldFormFormSerializer,
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
                start_time = time.time()

                current_event = scouting.util.get_current_event()

                print("--- %s current_event seconds ---" % (time.time() - start_time))
                start_time = time.time()

                seasons = scouting.util.get_all_seasons()

                print("--- %s seasons seconds ---" % (time.time() - start_time))
                start_time = time.time()

                events = scouting.util.get_all_events()

                print("--- %s events seconds ---" % (time.time() - start_time))
                start_time = time.time()

                teams = scouting.util.get_teams(True)

                print("--- %s teams seconds ---" % (time.time() - start_time))
                start_time = time.time()

                matches = scouting.util.get_matches(current_event)

                print("--- %s matches seconds ---" % (time.time() - start_time))
                start_time = time.time()

                schedules = scouting.util.get_current_schedule_parsed()

                print("--- %s schedules seconds ---" % (time.time() - start_time))
                start_time = time.time()

                scout_field_schedules = (
                    scouting.util.get_current_scout_field_schedule_parsed()
                )

                print("--- %s scout_field_schedules seconds ---" % (time.time() - start_time))
                start_time = time.time()

                schedule_types = scouting.util.get_schedule_types()

                print("--- %s schedule_types seconds ---" % (time.time() - start_time))
                start_time = time.time()

                team_notes = scouting.strategizing.util.get_team_notes(event=current_event)

                print("--- %s team_notes seconds ---" % (time.time() - start_time))
                start_time = time.time()

                match_strategies = scouting.strategizing.util.get_match_strategies(event=current_event)

                print("--- %s match_strategies seconds ---" % (time.time() - start_time))
                start_time = time.time()

                field_form_form = scouting.field.util.get_field_form()

                print("--- %s field_form_form seconds ---" % (time.time() - start_time))
                start_time = time.time()

                alliance_selections = scouting.strategizing.util.get_alliance_selections()

                print("--- %s alliance_selections seconds ---" % (time.time() - start_time))

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
