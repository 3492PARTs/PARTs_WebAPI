import datetime

import pytz
from django.db import IntegrityError
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.utils import json

from api.api.serializers import *
from api.auth.serializers import PhoneTypeSerializer
from api.api.models import *
from api.auth import send_email
from rest_framework.views import APIView
from api.auth.security import *
import requests

auth_obj = 2


class GetAdminInit(APIView):
    """
    API endpoint to get all the init values for the scout admin screen
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_init(self):
        return True

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                req = self.get_init()
                serializer = ScoutAdminInitSerializer(req)
                return Response(serializer.data)
            except Exception as e:
                return ret_message('An error occurred while initializing.', True, 'GetScoutAdminInit', request.user.id,
                                   e)
        else:
            return ret_message('You do not have access.', True, 'GetScoutAdminInit', request.user.id)