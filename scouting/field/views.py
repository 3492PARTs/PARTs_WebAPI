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
from .serializers import ScoutFieldResultsSerializer
from django.db.models import Q
from rest_framework.response import Response
from django.utils import timezone

auth_obj = "scoutfield"
auth_view_obj = "scoutFieldResults"
app_url = "scouting/field/"


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
