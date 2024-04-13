from rest_framework.response import Response
from rest_framework.views import APIView


app_url = "public/"


class APIStatus(APIView):
    """
    API endpoint to get if the api is available
    """

    def get(self, request, format=None):
        return Response(200)
