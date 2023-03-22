import datetime

from django.db.models.functions import Lower
from django.utils import timezone
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

from user.models import User
from .serializers import InitSerializer
from scouting.models import ScoutFieldSchedule, Event, Schedule, ScheduleType
from rest_framework.views import APIView
from general.security import has_access, ret_message
from django.db.models import Q
from rest_framework.response import Response

auth_obj = 54
scheduling_auth_obj = 57
app_url = 'scouting/portal/'


class Init(APIView):
    """
    API endpoint to get the init values for the scout portal
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = 'init/'

    def get_init(self):
        user = self.request.user
        try:
            current_event = Event.objects.get(Q(current='y') & Q(void_ind='n'))
        except Exception as e:
            return ret_message('No event set, see an admin.', True, app_url + self.endpoint, self.request.user.id, e)

        users = None
        all_sfs_parsed = None
        all_sch_parsed = None
        schedule_types = None
        if has_access(self.request.user.id, scheduling_auth_obj):
            users = User.objects.filter(Q(is_active=True) & Q(
                date_joined__isnull=False)).order_by(Lower('first_name'), Lower('last_name'))

            all_sfs = ScoutFieldSchedule.objects.filter(
                Q(event=current_event) & Q(void_ind='n'))\
                .order_by('notification3', 'st_time')

            all_sfs_parsed = []
            for s in all_sfs:
                all_sfs_parsed.append(self.parse_sfs(s))

            all_sch = Schedule.objects.filter(Q(event=current_event) & Q(void_ind='n')).order_by('sch_typ', 'notified', 'st_time')
            all_sch_parsed = []
            for s in all_sch:
                all_sch_parsed.append(self.parse_sch(s))

            schedule_types = ScheduleType.objects.all().order_by('sch_nm')

        sfs = ScoutFieldSchedule.objects.filter(Q(event=current_event) &
                                                Q(end_time__gte=(timezone.now() + datetime.timedelta(hours=1))) &
                                                Q(void_ind='n') &
                                                Q(Q(red_one=user) | Q(red_two=user) | Q(red_three=user) |
                                                  Q(blue_one=user) | Q(blue_two=user) | Q(blue_three=user))
                                                ).order_by('notification3', 'st_time')

        sfs_parsed = []
        for s in sfs:
            sfs_parsed.append(self.parse_sfs(s))

        sch = Schedule.objects.filter(Q(event=current_event) & Q(user=user) &
                                      Q(end_time__gte=(timezone.now() + datetime.timedelta(hours=1))) & Q(void_ind='n'))\
            .order_by('notified', 'st_time')

        sch_parsed = []
        for s in sch:
            sch_parsed.append(self.parse_sch(s))

        return {'fieldSchedule': sfs_parsed, 'schedule': sch_parsed, 'allFieldSchedule': all_sfs_parsed,
                'allSchedule': all_sch_parsed, 'users': users, 'scheduleTypes': schedule_types}

    def parse_sfs(self, s):
        return {
                'scout_field_sch_id': s.scout_field_sch_id,
                'event_id': s.event_id,
                'st_time': s.st_time,
                'end_time': s.end_time,
                'notification1': s.notification1,
                'notification2': s.notification2,
                'notification3': s.notification3,
                'red_one_id': s.red_one,
                'red_two_id': s.red_two,
                'red_three_id': s.red_three,
                'blue_one_id': s.blue_one,
                'blue_two_id': s.blue_two,
                'blue_three_id': s.blue_three
            }

    def parse_sch(self, s):
        return {
                'sch_id': s.scout_field_sch_id,
                'sch_typ': s.sch_typ.sch_typ,
                'sch_nm': s.sch_typ.sch_nm,
                'event_id': s.event_id,
                'st_time': s.st_time,
                'end_time': s.end_time,
                'notified': s.notification1,
                'user': s.user,
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
                return ret_message('An error occurred while initializing.', True, app_url + self.endpoint,
                                   request.user.id, e)
        else:
            return ret_message('You do not have access,', True, app_url + self.endpoint, request.user.id)
