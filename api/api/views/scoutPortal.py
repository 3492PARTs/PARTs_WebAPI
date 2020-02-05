from datetime import datetime, timedelta

import pytz
from django.db import IntegrityError
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.utils import json

from api.api.serializers import *
from api.api.models import *
from api.auth.models import AuthUser
from api.auth import send_email
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from api.auth.security import *
import requests

class GetScoutPortalInit(APIView):
    """
    API endpoint to get all the init values for the scout admin screen
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_init(self, user_id):
        try:
            current_season = Season.objects.get(current='y')
        except Exception as e:
            current_season = Season()

        try:
            current_event = Event.objects.get(Q(season=current_season) & Q(current='y') & Q(void_ind='n'))
        except Exception as e:
            current_event = Event()

        time = datetime.now() - timedelta(hours=5)  # datetime.now(pytz.timezone('US/Eastern'))
        fieldSchedule = []
        sss = ScoutSchedule.objects.filter(Q(sq_typ_id='field') &
                                           Q(time__gte=time) &
                                           Q(user_id=user_id)).order_by('time', 'user')
        for ss in sss:
            fieldSchedule.append({
                'scout_sch_id': ss.scout_sch_id,
                'user': ss.user.first_name + ' ' + ss.user.last_name,
                'user_id': ss.user.id,
                'sq_typ': ss.sq_typ_id,
                'sq_nm': ss.sq_typ.sq_nm,
                'time': ss.time.strftime('%m/%d/%Y %I:%M %p'),
                'notified': ss.notified
            })

        pitSchedule = []
        sss = ScoutSchedule.objects.filter(Q(sq_typ_id='pit') &
                                           Q(time__gte=time) &
                                           Q(user_id=user_id)).order_by('time', 'user')
        for ss in sss:
            pitSchedule.append({
                'scout_sch_id': ss.scout_sch_id,
                'user': ss.user.first_name + ' ' + ss.user.last_name,
                'user_id': ss.user.id,
                'sq_typ': ss.sq_typ_id,
                'sq_nm': ss.sq_typ.sq_nm,
                'time': ss.time.strftime('%m/%d/%Y %I:%M %p'),
                'notified': ss.notified
            })

        pastSchedule = []
        sss = ScoutSchedule.objects.filter(Q(time__lt=time) &
                                           Q(user_id=user_id)).order_by(
            'time', 'user')
        for ss in sss:
            pastSchedule.append({
                'scout_sch_id': ss.scout_sch_id,
                'user': ss.user.first_name + ' ' + ss.user.last_name,
                'user_id': ss.user.id,
                'sq_typ': ss.sq_typ_id,
                'sq_nm': ss.sq_typ.sq_nm,
                'time': ss.time.strftime('%m/%d/%Y %I:%M %p'),
                'notified': ss.notified
            })

        return {'fieldSchedule': fieldSchedule, 'pitSchedule': pitSchedule, 'pastSchedule': pastSchedule}

    def get(self, request, format=None):
        if has_access(request.user.id, 2):
            try:
                req = self.get_init(request.user.id)
                serializer = ScoutPortalInitSerializer(req)
                return Response(serializer.data)
            except Exception as e:
                return ret_message('An error occurred while initializing', True, e)
        else:
            return ret_message('You do not have access', True)