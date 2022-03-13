from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from api.api.tba.serializers import EventUpdatedSerializer

from api.auth.security import ret_message

# Create your views here.


class EventScheduleUpdated(APIView):
    """API endpoint to receive a TBA webhook for event updated"""

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def save_scout_schedule(self, serializer):
        """
        if serializer.validated_data['st_time'] <= timezone.now():
            return ret_message('Start time can\'t be in the past.', True, 'api/scoutAdmin/PostSaveScoutFieldScheduleEntry',
                               self.request.user.id)
        """

        if serializer.validated_data['end_time'] <= serializer.validated_data['st_time']:
            return ret_message('End time can\'t come before start.', True, 'api/scoutAdmin/PostSaveScoutFieldScheduleEntry',
                               self.request.user.id)

        if serializer.validated_data.get('scout_field_sch_id', None) is None:
            serializer.save()
            return ret_message('Saved schedule entry successfully')
        else:
            sfs = ScoutFieldSchedule.objects.get(
                scout_field_sch_id=serializer.validated_data['scout_field_sch_id'])
            sfs.red_one = serializer.validated_data.get('red_one', None)
            sfs.red_two = serializer.validated_data.get('red_two', None)
            sfs.red_three = serializer.validated_data.get('red_three', None)
            sfs.blue_one = serializer.validated_data.get('blue_one', None)
            sfs.blue_two = serializer.validated_data.get('blue_two', None)
            sfs.blue_three = serializer.validated_data.get('blue_three', None)
            sfs.st_time = serializer.validated_data['st_time']
            sfs.end_time = serializer.validated_data['end_time']
            sfs.notified = 'n'
            sfs.void_ind = serializer.validated_data['void_ind']
            sfs.save()
            return ret_message('Updated schedule entry successfully')

    def post(self, request, format=None):
        serializer = EventUpdatedSerializer(data=request.data)
        if not serializer.is_valid():
            return ret_message('Invalid data', True, 'api/tba/EventScheduleUpdated', request.user.id,
                               serializer.errors)

        if has_access(request.user.id, auth_obj):
            try:
                req = self.save_scout_schedule(serializer)
                return req
            except Exception as e:
                return ret_message('An error occurred while saving the schedule entry.', True,
                                   'api/scoutAdmin/PostSaveScoutFieldScheduleEntry', request.user.id, e)
        else:
            return ret_message('You do not have access.', True, 'api/scoutAdmin/PostSaveScoutFieldScheduleEntry', request.user.id)
