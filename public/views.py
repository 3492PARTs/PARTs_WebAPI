from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings


app_url = "public/"


class APIStatusView(APIView):
    """
    API endpoint to get if the api is available
    """

    def get(self, request, format=None):
        return Response({"branch": settings.ENVIRONMENT, "version": settings.VERSION})


# Backward compatibility aliases (can be removed in future versions)
APIStatus = APIStatusView
