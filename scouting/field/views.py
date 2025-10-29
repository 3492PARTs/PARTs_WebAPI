from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

import scouting.field
import scouting.field.util
import scouting.util
import scouting.models
from rest_framework.views import APIView
from general.security import ret_message, access_response
from rest_framework.response import Response

from ..serializers import FieldFormFormSerializer

from .serializers import (
    ColSerializer,
    FieldResponseSerializer,
    FieldResponsesSerializer,
)

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
        def fun():
            serializer = FieldFormFormSerializer(
                scouting.field.util.get_field_form()
            )
            return Response(serializer.data)

        # Try first permission
        result = access_response(
            app_url + self.endpoint,
            request.user.id,
            auth_obj,
            "An error occurred while getting field form.",
            fun,
        )
        # If access denied, try second permission
        if result.data.get("error") and "do not have access" in result.data.get("retMessage", ""):
            return access_response(
                app_url + self.endpoint,
                request.user.id,
                auth_view_obj,
                "An error occurred while getting field form.",
                fun,
            )
        return result


class ResponseColumnsView(APIView):
    """
    API endpoint to get the result columns of field scouting
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "response-columns/"

    def get(self, request, format=None):
        def fun():
            req = scouting.field.util.get_table_columns(
                scouting.field.util.get_field_question_aggregates(
                    scouting.util.get_current_season()
                )
            )
            serializer = ColSerializer(req, many=True)
            return Response(serializer.data)

        # Try first permission
        result = access_response(
            app_url + self.endpoint,
            request.user.id,
            auth_obj,
            "An error occurred while getting response columns.",
            fun,
        )
        # If access denied, try second permission
        if result.data.get("error") and "do not have access" in result.data.get("retMessage", ""):
            return access_response(
                app_url + self.endpoint,
                request.user.id,
                auth_view_obj,
                "An error occurred while getting response columns.",
                fun,
            )
        return result


class ResponsesView(APIView):
    """
    API endpoint to get the results of field scouting
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "responses/"

    def get(self, request, format=None):
        def fun():
            req = scouting.field.util.get_responses(
                request.query_params.get("pg_num", 1),
                team=request.query_params.get("team", None),
                after_scout_field_id=request.query_params.get(
                    "after_scout_field_id", None
                ),
            )

            if type(req) == Response:
                return req

            serializer = FieldResponsesSerializer(req)
            return Response(serializer.data)

        # Try first permission
        result = access_response(
            app_url + self.endpoint,
            request.user.id,
            auth_obj,
            "An error occurred while getting responses.",
            fun,
        )
        # If access denied, try second permission
        if result.data.get("error") and "do not have access" in result.data.get("retMessage", ""):
            return access_response(
                app_url + self.endpoint,
                request.user.id,
                auth_view_obj,
                "An error occurred while getting responses.",
                fun,
            )
        return result


class CheckInView(APIView):
    """
    API endpoint to let a field scout check in for thier shift
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "check-in/"

    def get(self, request, format=None):
        def fun():
            sfs = scouting.util.get_scout_field_schedule(
                id=request.query_params.get("scout_field_sch_id", None)
            )
            return ret_message(
                scouting.field.util.check_in_scout(sfs, request.user.id)
            )

        return access_response(
            app_url + self.endpoint,
            request.user.id,
            auth_obj,
            "An error occurred while checking in the scout for their shift.",
            fun,
        )


class ScoutingResponsesView(APIView):
    """
    API endpoint to get the results of field scouting
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "scouting-responses/"

    def get(self, request, format=None):
        def fun():
            req = scouting.field.util.get_scouting_responses()

            if type(req) == Response:
                return req

            serializer = FieldResponseSerializer(req, many=True)
            return Response(serializer.data)

        # Try first permission
        result = access_response(
            app_url + self.endpoint,
            request.user.id,
            auth_obj,
            "An error occurred while getting responses.",
            fun,
        )
        # If access denied, try second permission
        if result.data.get("error") and "do not have access" in result.data.get("retMessage", ""):
            return access_response(
                app_url + self.endpoint,
                request.user.id,
                auth_view_obj,
                "An error occurred while getting responses.",
                fun,
            )
        return result
