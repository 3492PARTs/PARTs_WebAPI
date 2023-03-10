import datetime

import pytz
from django.db.models import Q, ExpressionWrapper, F, DurationField
from rest_framework.response import Response
from rest_framework.views import APIView

from general import send_email
from general.security import ret_message
from scouting.models import Event, ScoutFieldSchedule

app_url = 'public/'


class APIStatus(APIView):
    """
    API endpoint to get if the api is available
    """

    def get(self, request, format=None):
        return Response(200)


class NotifyUsers(APIView):
    """API endpoint to notify users"""

    endpoint = 'notify-users/'

    def notify_users(self):
        message = 'No notifications'
        event = Event.objects.get(Q(current='y') & Q(void_ind='n'))
        curr_time = datetime.datetime.utcnow().astimezone(pytz.timezone(event.timezone))
        sfs = ScoutFieldSchedule.objects.annotate(diff=ExpressionWrapper(F('st_time') - curr_time, output_field=DurationField()))\
            .filter(diff__lte=datetime.timedelta(1/48))\
            .filter(Q(event=event) & Q(notified='n') & Q(void_ind='n'))
        for sf in sfs:
            date_st_utc = sf.st_time.astimezone(pytz.utc)
            date_end_utc = sf.end_time.astimezone(pytz.utc)
            date_st_local = date_st_utc.astimezone(pytz.timezone(event.timezone))
            date_end_local = date_end_utc.astimezone(pytz.timezone(event.timezone))
            date_st_str = date_st_local.strftime("%m/%d/%Y, %I:%M%p")
            date_end_str = date_end_local.strftime("%m/%d/%Y, %I:%M%p")
            data = {
                'scout_location': 'Field',
                'scout_time_st': date_st_str,
                'scout_time_end': date_end_str,
                'lead_scout': 'system_message'
            }
            message = ''
            try:
                send_email.send_message(
                    sf.red_one.phone + sf.red_one.phone_type.phone_type, 'Time to Scout!', 'notify_scout', data)
                message += 'Notified: ' + sf.red_one.first_name + '\n'
            except Exception as e:
                message += 'Unable to notify: ' + \
                    (sf.red_one.first_name if sf.red_one is not None else "red one") + '\n'
            try:
                send_email.send_message(
                    sf.red_two.phone + sf.red_two.phone_type.phone_type, 'Time to Scout!', 'notify_scout', data)
                message += 'Notified: ' + sf.red_two.first_name + '\n'
            except Exception as e:
                message += 'Unable to notify: ' + \
                    (sf.red_two.first_name if sf.red_two is not None else "red two") + '\n'
            try:
                send_email.send_message(
                    sf.red_three.phone + sf.red_three.phone_type.phone_type, 'Time to Scout!', 'notify_scout', data)
                message += 'Notified: ' + sf.red_three.first_name + '\n'
            except Exception as e:
                message += 'Unable to notify: ' + \
                    (sf.red_three.first_name if sf.red_three is not None else "red three") + '\n'
            try:
                send_email.send_message(
                    sf.blue_one.phone + sf.blue_one.phone_type.phone_type, 'Time to Scout!', 'notify_scout', data)
                message += 'Notified: ' + sf.blue_one.first_name + '\n'
            except Exception as e:
                message += 'Unable to notify: ' + \
                    (sf.blue_one.first_name if sf.blue_one is not None else "blue one") + '\n'
            try:
                send_email.send_message(
                    sf.blue_two.phone + sf.blue_two.phone_type.phone_type, 'Time to Scout!', 'notify_scout', data)
                message += 'Notified: ' + sf.blue_two.first_name + '\n'
            except Exception as e:
                message += 'Unable to notify: ' + \
                    (sf.blue_two.first_name if sf.blue_two is not None else "blue two") + '\n'
            try:
                send_email.send_message(
                    sf.blue_three.phone + sf.blue_three.phone_type.phone_type, 'Time to Scout!', 'notify_scout', data)
                message += 'Notified: ' + sf.blue_three.first_name + '\n'
            except Exception as e:
                message += 'Unable to notify: ' + \
                    (sf.blue_three.first_name if sf.blue_three is not None else "blue three") + '\n'

            sf.notified = 'y'
            sf.save()

        return ret_message(message)

    def get(self, request, format=None):
        try:
            req = self.notify_users()
            return req
        except Exception as e:
            return ret_message('An error occurred while notifying the users.', True, app_url + self.endpoint,
                               0, e)
