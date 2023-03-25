import datetime

import pytz
from django.db.models import Q, ExpressionWrapper, F, DurationField
from rest_framework.response import Response
from rest_framework.views import APIView

from general import send_email
from general.security import ret_message
from scouting.models import Event, ScoutFieldSchedule, Schedule

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
        message = ''
        event = Event.objects.get(Q(current='y') & Q(void_ind='n'))
        curr_time = datetime.datetime.utcnow().astimezone(pytz.timezone(event.timezone))
        sfss_15 = ScoutFieldSchedule.objects.annotate(
            diff=ExpressionWrapper(F('st_time') - curr_time, output_field=DurationField()))\
            .filter(diff__lte=datetime.timedelta(minutes=17))\
            .filter(Q(event=event) & Q(notification1=False) & Q(void_ind='n'))

        sfss_5 = ScoutFieldSchedule.objects.annotate(
            diff=ExpressionWrapper(F('st_time') - curr_time, output_field=DurationField())) \
            .filter(diff__lte=datetime.timedelta(minutes=7)) \
            .filter(Q(event=event) & Q(notification2=False) & Q(void_ind='n'))

        sfss_now = ScoutFieldSchedule.objects.annotate(
            diff=ExpressionWrapper(F('st_time') - curr_time, output_field=DurationField())) \
            .filter(diff__lt=datetime.timedelta(minutes=5)) \
            .filter(Q(event=event) & Q(notification3=False) & Q(void_ind='n'))

        message += self.send_scout_notification(1, sfss_15, event)
        message += self.send_scout_notification(2, sfss_5, event)
        message += self.send_scout_notification(3, sfss_now, event)

        schs = Schedule.objects.annotate(
            diff=ExpressionWrapper(F('st_time') - curr_time, output_field=DurationField())) \
            .filter(diff__lt=datetime.timedelta(minutes=5)) \
            .filter(Q(event=event) & Q(notified=False) & Q(void_ind='n'))

        for sch in schs:
            date_st_utc = sch.st_time.astimezone(pytz.utc)
            date_end_utc = sch.end_time.astimezone(pytz.utc)
            date_st_local = date_st_utc.astimezone(pytz.timezone(event.timezone))
            date_end_local = date_end_utc.astimezone(pytz.timezone(event.timezone))
            date_st_str = date_st_local.strftime("%m/%d/%Y, %I:%M%p")
            date_end_str = date_end_local.strftime("%m/%d/%Y, %I:%M%p")
            data = {
                'location': sch.sch_typ.sch_nm,
                'scout_time_st': date_st_str,
                'scout_time_end': date_end_str,
                'lead_scout': 'automated_message'
            }
            try:
                send_email.send_message(
                    sch.user.phone + sch.user.phone_type.phone_type, 'Pit time!', 'notify_scout', data)
                message += 'Notified: ' + sch.user.first_name + ' : ' + sch.sch_typ.sch_nm + '\n'
            except Exception as e:
                message += 'Unable to notify: ' + \
                           (sch.user.first_name if sch.user is not None else "pit time user missing") + '\n'

        if message is '':
            message = 'No notifications'

        return ret_message(message)

    def send_scout_notification(self, notification, sfss, event):
        message = ''
        for sfs in sfss:
            date_st_utc = sfs.st_time.astimezone(pytz.utc)
            date_end_utc = sfs.end_time.astimezone(pytz.utc)
            date_st_local = date_st_utc.astimezone(pytz.timezone(event.timezone))
            date_end_local = date_end_utc.astimezone(pytz.timezone(event.timezone))
            date_st_str = date_st_local.strftime("%m/%d/%Y, %I:%M%p")
            date_end_str = date_end_local.strftime("%m/%d/%Y, %I:%M%p")
            data = {
                'scout_location': 'Field',
                'scout_time_st': date_st_str,
                'scout_time_end': date_end_str,
                'lead_scout': 'automated_message'
            }
            try:
                send_email.send_message(
                    sfs.red_one.phone + sfs.red_one.phone_type.phone_type, 'Time to Scout!', 'notify_scout', data)
                message += 'Notified: ' + sfs.red_one.first_name + '\n'
            except Exception as e:
                message += 'Unable to notify: ' + \
                           (sfs.red_one.first_name if sfs.red_one is not None else "red one") + '\n'
            try:
                send_email.send_message(
                    sfs.red_two.phone + sfs.red_two.phone_type.phone_type, 'Time to Scout!', 'notify_scout', data)
                message += 'Notified: ' + sfs.red_two.first_name + '\n'
            except Exception as e:
                message += 'Unable to notify: ' + \
                           (sfs.red_two.first_name if sfs.red_two is not None else "red two") + '\n'
            try:
                send_email.send_message(
                    sfs.red_three.phone + sfs.red_three.phone_type.phone_type, 'Time to Scout!', 'notify_scout', data)
                message += 'Notified: ' + sfs.red_three.first_name + '\n'
            except Exception as e:
                message += 'Unable to notify: ' + \
                           (sfs.red_three.first_name if sfs.red_three is not None else "red three") + '\n'
            try:
                send_email.send_message(
                    sfs.blue_one.phone + sfs.blue_one.phone_type.phone_type, 'Time to Scout!', 'notify_scout', data)
                message += 'Notified: ' + sfs.blue_one.first_name + '\n'
            except Exception as e:
                message += 'Unable to notify: ' + \
                           (sfs.blue_one.first_name if sfs.blue_one is not None else "blue one") + '\n'
            try:
                send_email.send_message(
                    sfs.blue_two.phone + sfs.blue_two.phone_type.phone_type, 'Time to Scout!', 'notify_scout', data)
                message += 'Notified: ' + sfs.blue_two.first_name + '\n'
            except Exception as e:
                message += 'Unable to notify: ' + \
                           (sfs.blue_two.first_name if sfs.blue_two is not None else "blue two") + '\n'
            try:
                send_email.send_message(
                    sfs.blue_three.phone + sfs.blue_three.phone_type.phone_type, 'Time to Scout!', 'notify_scout', data)
                message += 'Notified: ' + sfs.blue_three.first_name + '\n'
            except Exception as e:
                message += 'Unable to notify: ' + \
                           (sfs.blue_three.first_name if sfs.blue_three is not None else "blue three") + '\n'

            match notification:
                case 1:
                    sfs.notification1 = True
                case 2:
                    sfs.notification2 = True
                case 3:
                    sfs.notification3 = True
            sfs.save()

        return message
    def get(self, request, format=None):
        try:
            req = self.notify_users()
            return req
        except Exception as e:
            return ret_message('An error occurred while notifying the users.', True, app_url + self.endpoint,
                               0, e)
