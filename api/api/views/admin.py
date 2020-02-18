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

auth_obj = 7


class GetAdminInit(APIView):
    """
    API endpoint to get all the init values for the admin screen
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_init(self):
        users = AuthUser.objects.filter(Q(is_active=True) & Q(date_joined__isnull=False))# & ~Q(id=self.request.user.id))

        user_groups = AuthGroup.objects.all()

        phone_types = PhoneType.objects.all()

        return {'users': users, 'userGroups': user_groups, 'phoneTypes': phone_types}

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                req = self.get_init()
                serializer = AdminInitSerializer(req)
                return Response(serializer.data)
            except Exception as e:
                return ret_message('An error occurred while initializing.', True, 'GetAdminInit', request.user.id,
                                   e)
        else:
            return ret_message('You do not have access.', True, 'GetAdminInit', request.user.id)
