from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.conf import settings

from scouting.models import Season
from tba.serializers import (
    EventUpdatedSerializer,
    ScheduleUpdatedSerializer,
    VerificationMessageSerializer,
)

from rest_framework.views import APIView

import tba.util
import scouting.util
from general.security import ret_message, access_response

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
        def fun():
            req = tba.util.sync_season(request.query_params.get("season_id", None))
            return ret_message(req)

        return access_response(
            app_url + self.endpoint,
            request.user.id,
            auth_obj,
            "An error occurred while syncing the season.",
            fun,
        )


class SyncEventView(APIView):
    """
    API endpoint to sync an event
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "sync-event/"

    def get(self, request, format=None):
        def fun():
            return ret_message(
                tba.util.sync_event(
                    Season.objects.get(id=request.query_params["season_id"]),
                    request.query_params.get("event_cd", None),
                )
            )

        return access_response(
            app_url + self.endpoint,
            request.user.id,
            auth_obj,
            "An error occurred while syncing the event.",
            fun,
        )


class SyncMatchesView(APIView):
    """
    API endpoint to sync a match
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "sync-matches/"

    def get(self, request, format=None):
        def fun():
            req = tba.util.sync_matches(scouting.util.get_current_event())
            return ret_message(req)

        return access_response(
            app_url + self.endpoint,
            request.user.id,
            auth_obj,
            "An error occurred while syncing matches.",
            fun,
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
                message = tba.util.save_message(request.data)
                match request.data["message_type"]:
                    case "verification":
                        serializer = VerificationMessageSerializer(data=request.data)
                        if serializer.is_valid():
                            message.processed = "y"
                            message.save()
                            return Response(200)
                        else:
                            ret_message(
                                "Webhook Error - Verification",
                                True,
                                app_url + self.endpoint,
                                error_message=serializer.errors,
                            )
                            return Response(500)
                    case "match_score":
                        serializer = EventUpdatedSerializer(data=request.data)
                        if serializer.is_valid():
                            tba.util.save_tba_match(
                                serializer.validated_data["message_data"]["match"]
                            )
                            message.processed = "y"
                            message.save()
                            return Response(200)
                        else:
                            ret_message(
                                "Webhook Error - Match Score",
                                True,
                                app_url + self.endpoint,
                                error_message=serializer.errors,
                            )
                            return Response(500)
                    case "schedule_updated":
                        serializer = ScheduleUpdatedSerializer(data=request.data)
                        if serializer.is_valid():
                            event_key = serializer.validated_data["message_data"][
                                "event_key"
                            ]
                            season = scouting.util.get_or_create_season(event_key[:4])
                            tba.util.sync_event(season, event_key)
                            event = scouting.util.get_event(event_key)
                            tba.util.sync_matches(event)
                            message.processed = "y"
                            message.save()
                            return Response(200)
                        else:
                            ret_message(
                                "Webhook Error - Schedule Updated",
                                True,
                                app_url + self.endpoint,
                                error_message=serializer.errors,
                            )
                            return Response(500)
                    case _:
                        return Response(200)
            else:
                ret_message(
                    "Webhook Error",
                    True,
                    app_url + self.endpoint,
                    error_message="Unauthenticated",
                )
        except Exception as e:
            ret_message("Webhook Error", True, app_url + self.endpoint, exception=e)

        return Response(500)
