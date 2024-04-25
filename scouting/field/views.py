from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

import form.util
import scouting.field
import scouting.field.util
import scouting.util
import scouting.models
from scouting.models import (
    ScoutFieldSchedule,
    ScoutField,
    Match,
)
from rest_framework.views import APIView
from general.security import ret_message, has_access
from .serializers import (
    ScoutFieldInitSerializer,
    ScoutFieldResultsSerializer,
    ScoutFieldSerializer,
)
from django.db.models import Q
from rest_framework.response import Response
from django.utils import timezone

auth_obj = "scoutfield"
auth_view_obj = "scoutFieldResults"
app_url = "scouting/field/"


class Init(APIView):
    """
    API endpoint to get scout field inputs
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "init/"

    def get_questions(self):
        current_event = scouting.util.get_current_event()

        # scout_questions = form.util.get_questions('field', 'y')
        scout_questions = form.util.get_questions_with_conditions("field")

        sfss = ScoutFieldSchedule.objects.filter(
            Q(st_time__lte=timezone.now())
            & Q(end_time__gte=timezone.now())
            & Q(void_ind="n")
        )

        sfs = None
        for s in sfss:
            sfs = scouting.util.format_scout_field_schedule_entry(s)

        matches = Match.objects.filter(
            Q(event=current_event) & Q(comp_level_id="qm") & Q(void_ind="n")
        ).order_by("match_number")
        parsed_matches = []

        for m in matches:
            blue_one_id = (
                m.blue_one.team_no
                if self.get_team_match_field_result(m, m.blue_one.team_no) is None
                else None
            )
            blue_two_id = (
                m.blue_two.team_no
                if self.get_team_match_field_result(m, m.blue_two.team_no) is None
                else None
            )
            blue_three_id = (
                m.blue_three.team_no
                if self.get_team_match_field_result(m, m.blue_three.team_no) is None
                else None
            )
            red_one_id = (
                m.red_one.team_no
                if self.get_team_match_field_result(m, m.red_one.team_no) is None
                else None
            )
            red_two_id = (
                m.red_two.team_no
                if self.get_team_match_field_result(m, m.red_two.team_no) is None
                else None
            )
            red_three_id = (
                m.red_three.team_no
                if self.get_team_match_field_result(m, m.red_three.team_no) is None
                else None
            )

            if (
                blue_one_id is not None
                or blue_two_id is not None
                or blue_three_id is not None
                or red_one_id is not None
                or red_two_id is not None
                or red_three_id is not None
            ):
                parsed_matches.append(
                    {
                        "match_id": m.match_id,
                        "event_id": m.event.event_id,
                        "match_number": m.match_number,
                        "time": m.time,
                        "blue_one": blue_one_id,
                        "blue_two": blue_two_id,
                        "blue_three": blue_three_id,
                        "red_one": red_one_id,
                        "red_two": red_two_id,
                        "red_three": red_three_id,
                    }
                )

        return {
            "scoutQuestions": scout_questions,
            "scoutFieldSchedule": sfs,
            "matches": parsed_matches,
        }

    def get_team_match_field_result(self, m, team):
        res = ScoutField.objects.filter(Q(match=m) & Q(team_no=team) & Q(void_ind="n"))
        if res.count() > 0:
            return res
        else:
            return None

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                req = self.get_questions()

                if type(req) == Response:
                    return req

                serializer = ScoutFieldInitSerializer(req)
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


class Responses(APIView):
    """
    API endpoint to get the results of field scouting
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "responses/"

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj) or has_access(
            request.user.id, auth_view_obj
        ):
            try:
                req = scouting.field.util.get_responses(
                    self.request,
                    team=request.query_params.get("team", None),
                    after_date_time=request.query_params.get("after_date_time", None),
                )

                if type(req) == Response:
                    return req

                serializer = ScoutFieldResultsSerializer(req)
                return Response(serializer.data)
            except Exception as e:
                return ret_message(
                    "An error occurred while getting responses.",
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


class CheckIn(APIView):
    """
    API endpoint to let a field scout check in for thier shift
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "check-in/"

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                sfs = ScoutFieldSchedule.objects.get(
                    scout_field_sch_id=request.query_params.get(
                        "scout_field_sch_id", None
                    )
                )

                return ret_message(check_in_scout(sfs, request.user.id))
            except Exception as e:
                return ret_message(
                    "An error occurred while checking in the scout for their shift.",
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


def check_in_scout(sfs: ScoutFieldSchedule, user_id: int):
    check_in = False
    if sfs.red_one and not sfs.red_one_check_in and sfs.red_one.id == user_id:
        sfs.red_one_check_in = timezone.now()
        check_in = True
    elif sfs.red_two and not sfs.red_two_check_in and sfs.red_two.id == user_id:
        sfs.red_two_check_in = timezone.now()
        check_in = True
    elif sfs.red_three and not sfs.red_three_check_in and sfs.red_three.id == user_id:
        sfs.red_three_check_in = timezone.now()
        check_in = True
    elif sfs.blue_one and not sfs.blue_one_check_in and sfs.blue_one.id == user_id:
        sfs.blue_one_check_in = timezone.now()
        check_in = True
    elif sfs.blue_two and not sfs.blue_two_check_in and sfs.blue_two.id == user_id:
        sfs.blue_two_check_in = timezone.now()
        check_in = True
    elif (
        sfs.blue_three and not sfs.blue_three_check_in and sfs.blue_three.id == user_id
    ):
        sfs.blue_three_check_in = timezone.now()
        check_in = True

    if check_in:
        sfs.save()
        return "Successfully checked in scout for their shift."
    return ""
