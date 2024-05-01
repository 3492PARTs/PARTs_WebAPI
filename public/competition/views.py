from rest_framework.views import APIView
from django.db.models import Q
from rest_framework.response import Response

import scouting.util
from .serializers import CompetitionInformationSerializer
from scouting.models import Event, Match, Team

from general.security import ret_message

# Create your views here.
app_url = "public/competition/"


class Init(APIView):
    """API endpoint to tell the frontend if the competition page is active and its information"""

    endpoint = "init/"

    def get_competition_information(self):
        event = Event.objects.get(
            Q(current="y") & Q(competition_page_active="y") & Q(void_ind="n")
        )
        team3492 = Team.objects.get(team_no=3492)

        matches = Match.objects.filter(
            Q(event=event)
            & Q(void_ind="n")
            & Q(
                Q(red_one=team3492)
                | Q(red_two=team3492)
                | Q(red_three=team3492)
                | Q(blue_one=team3492)
                | Q(blue_two=team3492)
                | Q(blue_three=team3492)
            )
        ).order_by("comp_level__comp_lvl_order", "match_number")

        matches = list(scouting.util.parse_match(m) for m in matches)

        return {"event": event, "matches": matches}

    def get(self, request, format=None):
        try:
            req = self.get_competition_information()
            serializer = CompetitionInformationSerializer(req)
            return Response(serializer.data)
        except Exception as e:
            return ret_message(
                "An error occurred while getting competition page information.",
                True,
                app_url + self.endpoint,
                exception=e,
            )
