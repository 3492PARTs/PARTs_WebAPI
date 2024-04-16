from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from django.db.models import Q, Case, When

from general.security import has_access, ret_message
import scouting
from scouting.models import ScoutPit, Team
from scouting.serializers import TeamSerializer

auth_obj = "scouting"
app_url = "scouting/"


class Teams(APIView):
    """
    API endpoint to init form editor
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
                    return scouting.util.get_no_season_ret_message(
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
