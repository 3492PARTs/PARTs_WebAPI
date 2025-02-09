from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db import transaction

import form.util
from general.security import ret_message, has_access
import scouting.strategizing
from scouting.serializers import MatchStrategySerializer, TeamNoteSerializer, AllianceSelectionSerializer, \
    SaveMatchStrategySerializer
import scouting.strategizing.util
import scouting.util
from scouting.strategizing.serializers import HistogramSerializer, HistogramBinSerializer, PlotSerializer, \
    BoxAndWhiskerPlotSerializer, DashboardSerializer

auth_obj = "matchplanning"
auth_view_obj_scout_field = "scoutFieldResults"
app_url = "scouting/strategizing/"


class TeamNoteView(APIView):
    """API endpoint to get team notes"""

    endpoint = "team-notes/"
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        try:
            if has_access(request.user.id, auth_obj) or has_access(
                request.user.id, auth_view_obj_scout_field
            ):
                req = scouting.strategizing.util.get_team_notes(
                    request.query_params.get("team_no", None),
                    scouting.util.get_current_event()
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
        serializer = TeamNoteSerializer(data=request.data)
        if not serializer.is_valid():
            return ret_message(
                "Invalid data",
                True,
                app_url + self.endpoint,
                request.user.id,
                error_message=serializer.errors,
            )

        if has_access(request.user.id, auth_obj):
            try:
                req = scouting.strategizing.util.save_note(
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


class MatchStrategyView(APIView):
    """API endpoint to get match strategies"""

    endpoint = "match-strategy/"
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        try:
            if has_access(request.user.id, auth_obj):
                req = scouting.strategizing.util.get_match_strategies(
                    request.query_params.get("match_id", None)
                )
                if request.query_params.get("match_id", None) is not None:
                    serializer = MatchStrategySerializer(req)
                else:
                    serializer = MatchStrategySerializer(req, many=True)
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
                "An error occurred while getting match strategy.",
                True,
                app_url + self.endpoint,
                exception=e,
            )

    def post(self, request, format=None):
        serializer = SaveMatchStrategySerializer(data=request.data)
        if not serializer.is_valid():
            return ret_message(
                "Invalid data",
                True,
                app_url + self.endpoint,
                request.user.id,
                error_message=serializer.errors,
            )

        if has_access(request.user.id, auth_obj):
            try:
                with transaction.atomic():
                    scouting.strategizing.util.save_match_strategy(serializer.data, request.data.get("img", None))
                return ret_message("Strategy saved successfully")
            except Exception as e:
                return ret_message(
                    "An error occurred while saving match strategy.",
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


class AllianceSelectionView(APIView):
    """API endpoint to manage alliance selections"""

    endpoint = "alliance-selection/"
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        try:
            if has_access(request.user.id, auth_obj):
                req = scouting.strategizing.util.get_alliance_selections()
                serializer = AllianceSelectionSerializer(req, many=True)
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
                "An error occurred while getting alliance selections.",
                True,
                app_url + self.endpoint,
                exception=e,
            )

    def post(self, request, format=None):
        serializer = AllianceSelectionSerializer(data=request.data, many=True)
        if not serializer.is_valid():
            return ret_message(
                "Invalid data",
                True,
                app_url + self.endpoint,
                request.user.id,
                error_message=serializer.errors,
            )

        if has_access(request.user.id, auth_obj):
            try:
                scouting.strategizing.util.save_alliance_selections(serializer.data)
                return ret_message("Alliance selection successfully")
            except Exception as e:
                return ret_message(
                    "An error occurred while saving alliance selections.",
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


class GraphTeamView(APIView):
    """API endpoint to manage alliance selections"""

    endpoint = "graph-team/"
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        try:
            if has_access(request.user.id, auth_obj):
                data = scouting.strategizing.util.graph_team(2, 3492)
                serializer = HistogramSerializer(data, many=True)
                #serializer = HistogramBinSerializer(data, many=True)
                #serializer = PlotSerializer(data, many=True)
                #serializer = BoxAndWhiskerPlotSerializer(data, many=True)
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
                "An error occurred while graphing.",
                True,
                app_url + self.endpoint,
                exception=e,
            )


class DashboardView(APIView):
    """
    API endpoint to manage dashboards
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "dashboard/"


    def get(self, request, format=None):
        try:
            if has_access(request.user.id, auth_obj):
                dashboard = scouting.strategizing.util.get_dashboard(request.user.id)
                serializer = DashboardSerializer(dashboard)
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
                "An error occurred while getting the dashboard.",
                True,
                app_url + self.endpoint,
                -1,
                e,
            )


    def post(self, request, format=None):
        try:
            if has_access(request.user.id, auth_obj):
                serializer = DashboardSerializer(data=request.data)
                if not serializer.is_valid():
                    return ret_message(
                        "Invalid data",
                        True,
                        app_url + self.endpoint,
                        request.user.id,
                        error_message=serializer.errors,
                    )

                scouting.strategizing.util.save_dashboard(serializer.validated_data, request.user.id)

                return ret_message("Saved dashboard successfully.")
            else:
                return ret_message(
                    "You do not have access.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                )
        except Exception as e:
            return ret_message(
                "An error occurred while saving dashboard.",
                True,
                app_url + self.endpoint,
                request.user.id,
                e,
            )