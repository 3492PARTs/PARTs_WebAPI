from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

import scouting
import scouting.pit
import scouting.pit.util
import scouting.util
from .serializers import (
    PitTeamDataSerializer,
    PitResponsesSerializer,
)
from rest_framework.views import APIView
from general.security import ret_message, access_response
from rest_framework.response import Response

auth_obj = "scoutpit"
auth_view_obj = "scoutPitResults"
app_url = "scouting/pit/"


class SavePictureView(APIView):
    """
    API endpoint to save a robot picture
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "save-picture/"

    def post(self, request, format=None):
        def fun():
            file_obj = request.FILES["file"]
            ret = scouting.pit.util.save_robot_picture(
                file_obj, request.data.get("team_no", ""), request.data.get("pit_image_typ", ""), request.data.get("img_title", "")
            )
            return ret

        return access_response(
            app_url + self.endpoint,
            request.user.id,
            auth_obj,
            "An error occurred while saving robot picture.",
            fun,
        )


class ResponsesView(APIView):
    """
    API endpoint to get scout pit results for the selected teams
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "responses/"

    def get(self, request, format=None):
        def fun():
            ret = scouting.pit.util.get_responses(
                request.query_params.get("team", None)
            )

            if type(ret) == Response:
                return ret

            serializer = PitResponsesSerializer(ret)
            return Response(serializer.data)

        # Try first permission
        result = access_response(
            app_url + self.endpoint,
            request.user.id,
            auth_obj,
            "An error occurred while getting pit responses.",
            fun,
        )
        # If access denied, try second permission
        if result.data.get("error") and "do not have access" in result.data.get("retMessage", ""):
            result = access_response(
                app_url + self.endpoint,
                request.user.id,
                auth_view_obj,
                "An error occurred while getting pit responses.",
                fun,
            )
            # If still access denied, try third permission
            if result.data.get("error") and "do not have access" in result.data.get("retMessage", ""):
                return access_response(
                    app_url + self.endpoint,
                    request.user.id,
                    "scoutFieldResults",
                    "An error occurred while getting pit responses.",
                    fun,
                )
        return result


class SetDefaultPitImageView(APIView):
    """
    API endpoint to set a default image for a team's pit scouting result
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "set-default-pit-image/"

    def get(self, request, format=None):
        def fun():
            scouting.pit.util.set_default_team_image(
                request.query_params.get("scout_pit_img_id", None)
            )
            return ret_message("Successfully set the default image.")

        return access_response(
            app_url + self.endpoint,
            request.user.id,
            auth_obj,
            "An error occurred while getting team data.",
            fun,
        )


class TeamDataView(APIView):
    """
    API endpoint to get scout pit team data
    for an individual team, used to get the data for the scouting screen not results screen
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "team-data/"

    def get(self, request, format=None):
        def fun():
            serializer = PitTeamDataSerializer(
                scouting.pit.util.get_team_data(
                    request.query_params.get("team_num", None)
                )
            )
            return Response(serializer.data)

        return access_response(
            app_url + self.endpoint,
            request.user.id,
            auth_obj,
            "An error occurred while getting team data.",
            fun,
        )
