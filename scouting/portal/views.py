from pytz import timezone
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

from .serializers import InitSerializer
from scouting.models import ScoutFieldSchedule, Event
from rest_framework.views import APIView
from general.security import has_access, ret_message
from django.db.models import Q
from rest_framework.response import Response

auth_obj = 54
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

        sfs = ScoutFieldSchedule.objects.filter(Q(event=current_event) & Q(end_time__gte=timezone.now()) & Q(void_ind='n') & Q(Q(red_one=user) | Q(
            red_two=user) | Q(red_three=user) | Q(blue_one=user) | Q(blue_two=user) | Q(blue_three=user))).order_by('st_time')

        # TODO REmove sss = ScoutFieldSchedule.objects.filter((Q(st_time__gte=time) | (Q(st_time__lte=time) & Q(end_time__gte=time))) & Q(user_id=user_id) & Q(void_ind='n')).order_by('st_time', 'user')
        """
        for ss in sss:
            fieldSchedule.append({
                'scout_sch_id': ss.scout_sch_id,
                'user': ss.user.first_name + ' ' + ss.user.last_name,
                'user_id': ss.user.id,
                'sq_typ': ss.sq_typ_id,
                'sq_nm': ss.sq_typ.sq_nm,
                'st_time': ss.st_time.astimezone(pytz.timezone('US/Eastern')).strftime('%m/%d/%Y %I:%M %p'),
                'end_time': ss.end_time.astimezone(pytz.timezone('US/Eastern')).strftime('%m/%d/%Y %I:%M %p'),
                'notified': ss.notified,
                'void_ind': ss.void_ind,
                'st_time_str': ss.st_time.astimezone(pytz.timezone('US/Eastern')).strftime('%m/%d/%Y %I:%M %p'),
                'end_time_str': ss.end_time.astimezone(pytz.timezone('US/Eastern')).strftime('%m/%d/%Y %I:%M %p'),
            })

        pitSchedule = []
        sss = ScoutPitSchedule.objects.filter((Q(st_time__gte=time) | (Q(st_time__lte=time) & Q(end_time__gte=time))) &
                                              Q(user_id=user_id) & Q(void_ind='n')).order_by('st_time', 'user')
        for ss in sss:
            pitSchedule.append({
                'scout_sch_id': ss.scout_sch_id,
                'user': ss.user.first_name + ' ' + ss.user.last_name,
                'user_id': ss.user.id,
                'sq_typ': ss.sq_typ_id,
                'sq_nm': ss.sq_typ.sq_nm,
                'st_time': ss.st_time.astimezone(pytz.timezone('US/Eastern')).strftime('%m/%d/%Y %I:%M %p'),
                'end_time': ss.end_time.astimezone(pytz.timezone('US/Eastern')).strftime('%m/%d/%Y %I:%M %p'),
                'notified': ss.notified,
                'void_ind': ss.void_ind,
                'st_time_str': ss.st_time.astimezone(pytz.timezone('US/Eastern')).strftime('%m/%d/%Y %I:%M %p'),
                'end_time_str': ss.end_time.astimezone(pytz.timezone('US/Eastern')).strftime('%m/%d/%Y %I:%M %p'),
            })

        
        pastSchedule = []
        sss = ScoutSchedule.objects.filter(Q(end_time__lt=time) &
                                           Q(user_id=user_id) & Q(void_ind='n')).order_by('st_time', 'user')
        for ss in sss:
            pastSchedule.append({
                'scout_sch_id': ss.scout_sch_id,
                'user': ss.user.first_name + ' ' + ss.user.last_name,
                'user_id': ss.user.id,
                'sq_typ': ss.sq_typ_id,
                'sq_nm': ss.sq_typ.sq_nm,
                'st_time': ss.st_time.astimezone(pytz.timezone('US/Eastern')).strftime('%m/%d/%Y %I:%M %p'),
                'end_time': ss.end_time.astimezone(pytz.timezone('US/Eastern')).strftime('%m/%d/%Y %I:%M %p'),
                'notified': ss.notified,
                'void_ind': ss.void_ind,
                'st_time_str': ss.st_time.astimezone(pytz.timezone('US/Eastern')).strftime('%m/%d/%Y %I:%M %p'),
                'end_time_str': ss.end_time.astimezone(pytz.timezone('US/Eastern')).strftime('%m/%d/%Y %I:%M %p'),
            })
        """
        return {'fieldSchedule': sfs}  # , 'pitSchedule': pitSchedule}

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
