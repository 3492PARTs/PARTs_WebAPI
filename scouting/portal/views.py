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


class SaveScheduleEntry(APIView):
    """API endpoint to save a schedule entry"""

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "save-schedule-entry/"

    def save_schedule(self, serializer):
        """
        if serializer.validated_data['st_time'] <= timezone.now():
            return ret_message('Start time can\'t be in the past.', True, app_url + self.endpoint,
                               self.request.user.id)
        """

        if (
            serializer.validated_data["end_time"]
            <= serializer.validated_data["st_time"]
        ):
            return ret_message(
                "End time can't come before start.",
                True,
                app_url + self.endpoint,
                self.request.user.id,
            )

        if serializer.validated_data.get("sch_id", None) is None:
            serializer.save()
            return ret_message("Saved schedule entry successfully")
        else:
            s = Schedule.objects.get(sch_id=serializer.validated_data["sch_id"])
            s.user_id = serializer.validated_data.get("user", None)
            s.sch_typ_id = serializer.validated_data.get("sch_typ", None)
            s.st_time = serializer.validated_data["st_time"]
            s.end_time = serializer.validated_data["end_time"]
            s.void_ind = serializer.validated_data["void_ind"]
            s.save()
            return ret_message("Updated schedule entry successfully")

    def post(self, request, format=None):
        serializer = ScheduleSaveSerializer(data=request.data)
        if not serializer.is_valid():
            return ret_message(
                "Invalid data",
                True,
                app_url + self.endpoint,
                request.user.id,
                serializer.errors,
            )

        if has_access(request.user.id, scheduling_auth_obj):
            try:
                req = self.save_schedule(serializer)
                return req
            except Exception as e:
                return ret_message(
                    "An error occurred while saving the schedule entry.",
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


class NotifyUser(APIView):
    """API endpoint to notify users"""

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "notify-user/"

    def notify_user(self, id):
        sch = Schedule.objects.get(sch_id=id)
        message = alerts.util.stage_schedule_alert(sch)
        alerts.util.send_alerts()
        sch.notified = True
        sch.save()

        return ret_message(message)

    def get(self, request, format=None):
        if has_access(request.user.id, scheduling_auth_obj):
            try:
                with transaction.atomic():
                    req = self.notify_user(request.query_params.get("id", None))
                    return req
            except Exception as e:
                return ret_message(
                    "An error occurred while notifying the user.",
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
