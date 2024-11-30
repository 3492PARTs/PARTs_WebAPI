from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.conf import settings

from tba.serializers import EventUpdatedSerializer, VerificationMessageSerializer

from rest_framework.views import APIView

import tba.util
from general.security import has_access, ret_message

auth_obj = "scoutadmin"
app_url = "tba/"


class SyncSeasonView(APIView):
    """
    API endpoint to sync a season
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "sync-season/"

    def get(self, request, format=None):
        try:
            if has_access(request.user.id, auth_obj):
                req = tba.util.sync_season(
                    request.query_params.get("season_id", None)
                )
                return ret_message(req)
            else:
                return ret_message(
                    "You do not have access.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                )
        except Exception as e:
            return ret_message(
                "An error occurred while syncing the season.",
                True,
                app_url + self.endpoint,
                request.user.id,
                e,
            )


class SyncEventView(APIView):
    """
    API endpoint to sync an event
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "sync-event/"

    def get(self, request, format=None):
        try:
            if has_access(request.user.id, auth_obj):
                return ret_message(
                    tba.util.sync_event(
                        request.query_params.get("event_cd", None)
                    )
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
                "An error occurred while syncing the event.",
                True,
                app_url + self.endpoint,
                request.user.id,
                e,
            )


class SyncMatchesView(APIView):
    """
    API endpoint to sync a match
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "sync-matches/"

    def get(self, request, format=None):
        try:
            if has_access(request.user.id, auth_obj):
                req = tba.util.sync_matches()
                return ret_message(req)
            else:
                return ret_message(
                    "You do not have access.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                )
        except Exception as e:
            return ret_message(
                "An error occurred while syncing matches.",
                True,
                app_url + self.endpoint,
                request.user.id,
                e,
            )


class SyncEventTeamInfoView(APIView):
    """
    API endpoint to sync the info for a teams at an event
    """

    # commented out so the server can call to update
    # authentication_classes = (JWTAuthentication,)
    # permission_classes = (IsAuthenticated,)
    endpoint = "sync-event-team-info/"

    def get(self, request, format=None):
        try:
            req = tba.util.sync_event_team_info(
                int(request.query_params.get("force", "0"))
            )
            return ret_message(req)
        except Exception as e:
            return ret_message(
                "An error occurred while syncing event team info.",
                True,
                app_url + self.endpoint,
                request.user.id,
                e,
            )


class Webhook(APIView):
    """API endpoint to receive a TBA webhook"""

    endpoint = "webhook/"

    def post(self, request, format=None):
        try:
            if tba.util.verify_tba_webhook_call(request):
                tba.util.save_message(request.data)
                match request.data["message_type"]:
                    case "verification":
                        serializer = VerificationMessageSerializer(data=request.data)
                        if serializer.is_valid():
                            return Response(200)
                        else:
                            ret_message('Webhook Error - Verification', True, app_url + self.endpoint, error_message=serializer.errors)
                            return Response(500)
                    case "match_score":
                        serializer = EventUpdatedSerializer(data=request.data)
                        if serializer.is_valid():
                            print(serializer.validated_data["message_data"]["match"])
                            tba.util.save_tba_match(serializer.validated_data["message_data"]["match"])
                            return Response(200)
                        else:
                            ret_message('Webhook Error - Match Score', True, app_url + self.endpoint, error_message=serializer.errors)
                            return Response(500)
                    case _:
                        return Response(200)
            else:
                ret_message('Webhook Error', True, app_url + self.endpoint, error_message="Unauthenticated")
        except Exception as e:
            ret_message('Webhook Error', True, app_url + self.endpoint, exception=e,
                        error_message=request.data)

        return Response(500)
