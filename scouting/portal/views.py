import datetime

from django.db import transaction
from django.utils import timezone
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

import alerts.apps
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


class Init(APIView):
    """
    API endpoint to get the init values for the scout portal
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "init/"

    def get_init(self):
        try:
            current_event = Event.objects.get(Q(current="y") & Q(void_ind="n"))
        except Exception as e:
            return ret_message(
                "No event set, see an admin.",
                True,
                app_url + self.endpoint,
                self.request.user.id,
                e,
            )

        users = None
        all_sfs_parsed = None
        schedule_types = None
        all_sch = []
        if has_access(self.request.user.id, scheduling_auth_obj):
            users = user.util.get_users(1, 1)

            all_sfs = ScoutFieldSchedule.objects.filter(
                Q(event=current_event) & Q(void_ind="n")
            ).order_by("notification3", "st_time")

            all_sfs_parsed = []
            for s in all_sfs:
                all_sfs_parsed.append(self.parse_sfs(s))

            schedule_types = ScheduleType.objects.all().order_by("sch_nm")

            for st in schedule_types:

                sch = Schedule.objects.filter(
                    Q(event=current_event) & Q(sch_typ=st) & Q(void_ind="n")
                ).order_by("sch_typ", "notified", "st_time")
                sch_parsed = []
                for s in sch:
                    sch_parsed.append(self.parse_sch(s))

                all_sch.append({"sch_typ": st, "sch": sch_parsed})

        sfs = ScoutFieldSchedule.objects.filter(
            Q(event=current_event)
            & Q(end_time__gte=(timezone.now() - datetime.timedelta(hours=1)))
            & Q(void_ind="n")
            & Q(
                Q(red_one=self.request.user)
                | Q(red_two=self.request.user)
                | Q(red_three=self.request.user)
                | Q(blue_one=self.request.user)
                | Q(blue_two=self.request.user)
                | Q(blue_three=self.request.user)
            )
        ).order_by("notification3", "st_time")

        sfs_parsed = []
        for s in sfs:
            sfs_parsed.append(self.parse_sfs(s))

        sch = Schedule.objects.filter(
            Q(event=current_event) & Q(user=self.request.user) & Q(void_ind="n")
        ).order_by("notified", "st_time")

        sch_parsed = []
        for s in sch:
            sch_parsed.append(self.parse_sch(s))

        return {
            "fieldSchedule": sfs_parsed,
            "schedule": sch_parsed,
            "allFieldSchedule": all_sfs_parsed,
            "allSchedule": all_sch,
            "users": users,
            "scheduleTypes": schedule_types,
        }

    def parse_sfs(self, s):
        return {
            "scout_field_sch_id": s.scout_field_sch_id,
            "event_id": s.event_id,
            "st_time": s.st_time,
            "end_time": s.end_time,
            "notification1": s.notification1,
            "notification2": s.notification2,
            "notification3": s.notification3,
            "red_one_id": s.red_one,
            "red_two_id": s.red_two,
            "red_three_id": s.red_three,
            "blue_one_id": s.blue_one,
            "blue_two_id": s.blue_two,
            "blue_three_id": s.blue_three,
            "scouts": "R1: "
            + (
                ""
                if s.red_one is None
                else s.red_one.first_name + " " + s.red_one.last_name[0:1]
            )
            + "\nR2: "
            + (
                ""
                if s.red_two is None
                else s.red_two.first_name + " " + s.red_two.last_name[0:1]
            )
            + "\nR3: "
            + (
                ""
                if s.red_three is None
                else s.red_three.first_name + " " + s.red_three.last_name[0:1]
            )
            + "\nB1: "
            + (
                ""
                if s.blue_one is None
                else s.blue_one.first_name + " " + s.blue_one.last_name[0:1]
            )
            + "\nB2: "
            + (
                ""
                if s.blue_two is None
                else s.blue_two.first_name + " " + s.blue_two.last_name[0:1]
            )
            + "\nB3: "
            + (
                ""
                if s.blue_three is None
                else s.blue_three.first_name + " " + s.blue_three.last_name[0:1]
            ),
        }

    def parse_sch(self, s):
        return {
            "sch_id": s.sch_id,
            "sch_typ": s.sch_typ.sch_typ,
            "sch_nm": s.sch_typ.sch_nm,
            "event_id": s.event_id,
            "st_time": s.st_time,
            "end_time": s.end_time,
            "notified": s.notified,
            "user": s.user,
            "user_name": s.user.first_name + " " + s.user.last_name,
        }

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                req = self.get_init()

                if isinstance(req, Response):
                    return req

                serializer = InitSerializer(req)
                return Response(serializer.data)
            except Exception as e:
                return ret_message(
                    "An error occurred while initializing.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                    e,
                )
        else:
            return ret_message(
                "You do not have access,",
                True,
                app_url + self.endpoint,
                request.user.id,
            )


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
