from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from general.security import ret_message, has_access
import scouting.matchplanning
from scouting.matchplanning.serializers import (
    SaveTeamNoteSerializer,
    TeamNoteSerializer,
)
import scouting.matchplanning.util
import scouting.util

auth_obj = "matchplanning"
auth_view_obj_scout_field = "scoutFieldResults"
app_url = "scouting/match-planning/"


class TeamNotesView(APIView):
    """API endpoint to get team notes"""

    endpoint = "team-notes/"
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        try:
            if has_access(request.user.id, auth_obj) or has_access(
                request.user.id, auth_view_obj_scout_field
            ):
                req = scouting.matchplanning.util.get_parsed_team_noes(
                    request.query_params.get("team_no", None)
                )
                serializer = TeamNoteSerializer(req, many=True)
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
                "An error occurred while getting team notes.",
                True,
                app_url + self.endpoint,
                exception=e,
            )

    def post(self, request, format=None):
        serializer = SaveTeamNoteSerializer(data=request.data)
        if not serializer.is_valid():
            return ret_message(
                "Invalid data",
                True,
                app_url + self.endpoint,
                request.user.id,
                serializer.errors,
            )

        if has_access(request.user.id, auth_obj):
            try:
                req = scouting.matchplanning.util.save_note(
                    serializer.data, request.user
                )
                return req
            except Exception as e:
                return ret_message(
                    "An error occurred while saving note.",
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
