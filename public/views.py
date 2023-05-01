import datetime

import pytz
import requests
from django.db.models import Q, ExpressionWrapper, F, DurationField
from rest_framework.response import Response
from rest_framework.views import APIView

from general import send_message
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
            diff=ExpressionWrapper(F('st_time') - curr_time, output_field=DurationField())) \
            .filter(diff__lte=datetime.timedelta(minutes=17)) \
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
            .filter(diff__lte=datetime.timedelta(minutes=6)) \
            .filter(Q(event=event) & Q(notified=False) & Q(void_ind='n')).order_by('sch_typ__sch_typ', 'st_time')

        discord_message = ''
        sch_typ = ''
        st_time = None
        for i in range(len(schs) + 1):
            if len(schs) == 0:
                break

            sch = None
            try:
                sch = schs[i]
            except IndexError:
                sch = None
            finally:
                if sch is None or \
                        (sch_typ != '' and sch_typ != sch.sch_typ.sch_typ) or \
                        (st_time is not None and st_time != sch.st_time):
                    sch_typ = ''
                    st_time = None
                    discord_message = discord_message[0:len(discord_message) - 2]
                    send_message.send_discord_notification(discord_message)
                    discord_message = ''
                    message += 'Discord Message Sent\n'

                if sch is None:
                    break

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
                send_message.send_email(
                    sch.user.phone + sch.user.phone_type.phone_type, 'Pit time!', 'notify_schedule', data)
                message += 'Phone Notified: ' + sch.user.first_name + ' : ' + sch.sch_typ.sch_nm + '\n'
                sch.notified = True
                sch.save()
            except Exception as e:
                message += 'Phone unable to notify: ' + \
                           (sch.user.first_name if sch.user is not None else "pit time user missing") + '\n'

            if sch_typ == '' or st_time is None:
                sch_typ = sch.sch_typ.sch_typ
                st_time = sch.st_time
                discord_message = f'Scheduled time in the pit, for {sch.sch_typ.sch_nm} from ' \
                                  f'{date_st_str} to {date_end_str} : '

            if sch_typ == sch.sch_typ.sch_typ and st_time == sch.st_time:
                discord_message += (f'<@{sch.user.discord_user_id}>' if sch.user.discord_user_id is not None
                                    else sch.user.first_name) + ', '
                sch.notified = True
                sch.save()
                message += 'Discord Notified: ' + sch.user.first_name + ' : ' + sch.sch_typ.sch_nm + '\n'

        if message == '':
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
                send_message.send_email(
                    sfs.red_one.phone + sfs.red_one.phone_type.phone_type, 'Time to Scout!', 'notify_scout', data)
                message += 'Phone Notified scouting: ' + sfs.red_one.first_name + '\n'
            except Exception as e:
                message += 'Phone Unable to notify scouting: ' + \
                           (sfs.red_one.first_name if sfs.red_one is not None else "red one") + '\n'
            try:
                send_message.send_email(
                    sfs.red_two.phone + sfs.red_two.phone_type.phone_type, 'Time to Scout!', 'notify_scout', data)
                message += 'Phone Notified scouting: ' + sfs.red_two.first_name + '\n'
            except Exception as e:
                message += 'Phone Unable to notify scouting: ' + \
                           (sfs.red_two.first_name if sfs.red_two is not None else "red two") + '\n'
            try:
                send_message.send_email(
                    sfs.red_three.phone + sfs.red_three.phone_type.phone_type, 'Time to Scout!', 'notify_scout', data)
                message += 'Phone Notified scouting: ' + sfs.red_three.first_name + '\n'
            except Exception as e:
                message += 'Phone Unable to notify scouting: ' + \
                           (sfs.red_three.first_name if sfs.red_three is not None else "red three") + '\n'
            try:
                send_message.send_email(
                    sfs.blue_one.phone + sfs.blue_one.phone_type.phone_type, 'Time to Scout!', 'notify_scout', data)
                message += 'Phone Notified scouting: ' + sfs.blue_one.first_name + '\n'
            except Exception as e:
                message += 'Phone Unable to notify scouting: ' + \
                           (sfs.blue_one.first_name if sfs.blue_one is not None else "blue one") + '\n'
            try:
                send_message.send_email(
                    sfs.blue_two.phone + sfs.blue_two.phone_type.phone_type, 'Time to Scout!', 'notify_scout', data)
                message += 'Phone Notified scouting: ' + sfs.blue_two.first_name + '\n'
            except Exception as e:
                message += 'Phone Unable to notify scouting: ' + \
                           (sfs.blue_two.first_name if sfs.blue_two is not None else "blue two") + '\n'
            try:
                send_message.send_email(
                    sfs.blue_three.phone + sfs.blue_three.phone_type.phone_type, 'Time to Scout!', 'notify_scout', data)
                message += 'Phone Notified scouting: ' + sfs.blue_three.first_name + '\n'
            except Exception as e:
                message += 'Phone Unable to notify scouting: ' + \
                           (sfs.blue_three.first_name if sfs.blue_three is not None else "blue three") + '\n'

            warning_text = ''
            match notification:
                case 1:
                    sfs.notification1 = True
                    warning_text = ', 15 minute warning, '
                case 2:
                    sfs.notification2 = True
                    warning_text = ', 5 minute warning, '
                case 3:
                    sfs.notification3 = True

            discord_message = f'Scheduled time for scouting{warning_text}from ' \
                              f'{date_st_str} to {date_end_str} : '

            discord_message += ((f'<@{sfs.red_one.discord_user_id}>' if sfs.red_one.discord_user_id is not None
                                else sfs.red_one.first_name) if sfs.red_one is not None else "red one") + ', '

            discord_message += ((f'<@{sfs.red_two.discord_user_id}>' if sfs.red_two.discord_user_id is not None
                                 else sfs.red_two.first_name) if sfs.red_two is not None else "red two") + ', '

            discord_message += ((f'<@{sfs.red_three.discord_user_id}>' if sfs.red_three.discord_user_id is not None
                                 else sfs.red_three.first_name) if sfs.red_three is not None else "red three") + ', '

            discord_message += ((f'<@{sfs.blue_one.discord_user_id}>' if sfs.blue_one.discord_user_id is not None
                                 else sfs.blue_one.first_name) if sfs.blue_one is not None else "blue one") + ', '

            discord_message += ((f'<@{sfs.blue_two.discord_user_id}>' if sfs.blue_two.discord_user_id is not None
                                 else sfs.blue_two.first_name) if sfs.blue_two is not None else "blue two") + ', '

            discord_message += ((f'<@{sfs.blue_three.discord_user_id}>' if sfs.blue_three.discord_user_id is not None
                                 else sfs.blue_three.first_name) if sfs.blue_three is not None else "blue three")

            send_message.send_discord_notification(discord_message)

            sfs.save()

        return message

    def get(self, request, format=None):
        try:
            req = self.notify_users()
            return req
        except Exception as e:
            return ret_message('An error occurred while notifying the users.', True, app_url + self.endpoint,
                               0, e)
