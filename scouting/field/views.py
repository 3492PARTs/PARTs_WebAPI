from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

import scouting.field
import scouting.field.util
import scouting.util
import scouting.models
from rest_framework.views import APIView
from general.security import ret_message, has_access
from .serializers import ScoutFieldResultsSerializer, FormFieldFormSerializer
from rest_framework.response import Response

auth_obj = "scoutfield"
auth_view_obj = "scoutFieldResults"
app_url = "scouting/field/"


class FormView(APIView):
    """
    API endpoint to get the scouting form
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "form/"

    def get(self, request, format=None):
        try:
            if has_access(request.user.id, auth_obj) or has_access(
                request.user.id, auth_view_obj
            ):
                serializer = FormFieldFormSerializer(scouting.field.util.get_field_form())
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
                "An error occurred while getting field form.",
                True,
                app_url + self.endpoint,
                request.user.id,
                e,
            )


class ResponsesView(APIView):
    """
    API endpoint to get the results of field scouting
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "responses/"

    def get(self, request, format=None):
        try:
            if has_access(request.user.id, auth_obj) or has_access(
                request.user.id, auth_view_obj
            ):
                req = scouting.field.util.get_responses(
                    self.request,
                    team=request.query_params.get("team", None),
                    after_date_time=request.query_params.get("after_date_time", None),
                )

                if type(req) == Response:
                    return req

                serializer = ScoutFieldResultsSerializer(req)
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
                "An error occurred while getting responses.",
                True,
                app_url + self.endpoint,
                request.user.id,
                e,
            )


class CheckInView(APIView):
    """
    API endpoint to let a field scout check in for thier shift
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "check-in/"

    def get(self, request, format=None):
        try:
            if has_access(request.user.id, auth_obj):
                sfs = scouting.util.get_scout_field_schedule(
                    scout_field_sch_id=request.query_params.get(
                        "scout_field_sch_id", None
                    )
                )
                return ret_message(
                    scouting.field.util.check_in_scout(sfs, request.user.id)
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
                "An error occurred while checking in the scout for their shift.",
                True,
                app_url + self.endpoint,
                request.user.id,
                e,
            )
