from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from django.db.models import Q, Case, When

from general.security import has_access, ret_message
import scouting
from scouting.models import EventTeamInfo, Match, ScoutPit, Team
from scouting.serializers import MatchSerializer, SchedulesSerializer, TeamSerializer
import scouting.util

auth_obj = "scouting"
app_url = "scouting/"


class Teams(APIView):
    """
    API endpoint to get the current list of teams
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "teams/"

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                current_event = scouting.util.get_current_event()

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


class Matches(APIView):
    """
    API endpoint to get the current list of matches
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "matches/"

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


class Schedules(APIView):
    """
    API endpoint to get all schedules
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "schedules/"

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                types = scouting.util.get_schedule_types()
                sch = list(
                    scouting.util.parse_schedule(s)
                    for s in scouting.util.get_current_schedule(request)
                )
                field_sch = list(
                    scouting.util.parse_scout_field_schedule(s)
                    for s in scouting.util.get_current_scout_field_schedule(request)
                )

                serializer = SchedulesSerializer(
                    {
                        "schedule_types": types,
                        "schedule": sch,
                        "field_schedule": field_sch,
                    }
                )
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
