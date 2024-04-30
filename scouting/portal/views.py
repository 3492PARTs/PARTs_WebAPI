import datetime

from django.db import transaction
from django.utils import timezone
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

import alerts.apps
import scouting
import user
from .serializers import InitSerializer, ScheduleSaveSerializer
from scouting.models import ScoutFieldSchedule, Event, Schedule, ScheduleType
from rest_framework.views import APIView
from general.security import has_access, ret_message
from django.db.models import Q
from rest_framework.response import Response

auth_obj = "scoutPortal"
scheduling_auth_obj = "scheduling"
app_url = "scouting/portal/"

