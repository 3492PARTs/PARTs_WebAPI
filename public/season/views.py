from rest_framework.views import APIView
from rest_framework.response import Response

import scouting
from scouting.serializers import SeasonSerializer


from general.security import ret_message

# Create your views here.
app_url = "public/season/"


class CurrentSeasonView(APIView):
    """
    API endpoint to get the season
    """

    endpoint = "current/"

    def get(self, request, format=None):
        try:
            serializer = SeasonSerializer(scouting.util.get_current_season())

            return Response(serializer.data)
        except Exception as e:
            return ret_message(
                "An error occurred while getting the season.",
                True,
                app_url + self.endpoint,
                request.user.id,
                e,
            )
