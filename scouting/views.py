from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from django.db.models import Q, Case, When

from general.security import has_access, ret_message
import scouting
from scouting.models import Match, ScoutPit, Team
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
                current_season = scouting.util.get_current_season()

                if current_season is None:
                    return scouting.util.get_no_season_ret_message(
                        app_url + self.endpoint, self.request.user.id
                    )

                current_event = scouting.util.get_event(current_season, "y")

                if current_event is None:
                    return scouting.util.get_no_event_ret_message(
                        app_url + self.endpoint, self.request.user.id
                    )

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
                current_season = scouting.util.get_current_season()

                if current_season is None:
                    return scouting.util.get_no_season_ret_message(
                        app_url + self.endpoint, self.request.user.id
                    )

                current_event = scouting.util.get_event(current_season, "y")

                if current_event is None:
                    return scouting.util.get_no_event_ret_message(
                        app_url + self.endpoint, self.request.user.id
                    )

                matches = Match.objects.filter(
                    Q(event=current_event) & Q(void_ind="n")
                ).order_by("comp_level__comp_lvl_order", "match_number")

                parsed_matches = []
                for m in matches:
                    try:
                        eti_blue_one = m.blue_one.eventteaminfo_set.get(
                            Q(event=current_event) & Q(void_ind="n")
                        )
                    except:
                        eti_blue_one = None

                    try:
                        eti_blue_two = m.blue_two.eventteaminfo_set.get(
                            Q(event=current_event) & Q(void_ind="n")
                        )
                    except:
                        eti_blue_two = None

                    try:
                        eti_blue_three = m.blue_three.eventteaminfo_set.get(
                            Q(event=current_event) & Q(void_ind="n")
                        )
                    except:
                        eti_blue_three = None

                    try:
                        eti_red_one = m.red_one.eventteaminfo_set.get(
                            Q(event=current_event) & Q(void_ind="n")
                        )
                    except:
                        eti_red_one = None

                    try:
                        eti_red_two = m.red_two.eventteaminfo_set.get(
                            Q(event=current_event) & Q(void_ind="n")
                        )
                    except:
                        eti_red_two = None

                    try:
                        eti_red_three = m.red_three.eventteaminfo_set.get(
                            Q(event=current_event) & Q(void_ind="n")
                        )
                    except:
                        eti_red_three = None

                    parsed_matches.append(
                        {
                            "match_id": m.match_id,
                            "event_id": m.event.event_id,
                            "match_number": m.match_number,
                            "red_score": m.red_score,
                            "blue_score": m.blue_score,
                            "time": m.time,
                            "blue_one_id": m.blue_one.team_no,
                            "blue_one_rank": (
                                None if eti_blue_one is None else eti_blue_one.rank
                            ),
                            "blue_two_id": m.blue_two.team_no,
                            "blue_two_rank": (
                                None if eti_blue_two is None else eti_blue_two.rank
                            ),
                            "blue_three_id": m.blue_three.team_no,
                            "blue_three_rank": (
                                None if eti_blue_three is None else eti_blue_three.rank
                            ),
                            "red_one_id": m.red_one.team_no,
                            "red_one_rank": (
                                None if eti_red_one is None else eti_red_one.rank
                            ),
                            "red_two_id": m.red_two.team_no,
                            "red_two_rank": (
                                None if eti_red_two is None else eti_red_two.rank
                            ),
                            "red_three_id": m.red_three.team_no,
                            "red_three_rank": (
                                None if eti_red_three is None else eti_red_three.rank
                            ),
                            "comp_level": m.comp_level,
                            "scout_field_result": len(m.scoutfield_set.all()) > 0,
                        }
                    )

                serializer = MatchSerializer(parsed_matches, many=True)
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
