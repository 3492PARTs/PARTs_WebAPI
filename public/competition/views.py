from rest_framework.views import APIView
from rest_framework.response import Response


from .serializers import CompetitionInformationSerializer
from general.security import ret_message
import public.competition.util

# Create your views here.
app_url = "public/competition/"


class Init(APIView):
    """API endpoint to tell the frontend if the competition page is active and its information"""

    endpoint = "init/"

    def get(self, request, format=None):
        try:
            try:
                req = public.competition.util.get_competition_information()
                serializer = CompetitionInformationSerializer(req)
                return Response(serializer.data)
            except Exception as e:
                return ret_message("No event")
        except Exception as e:
            return ret_message(
                "An error occurred while getting competition page information.",
                True,
                app_url + self.endpoint,
                exception=e,
            )
