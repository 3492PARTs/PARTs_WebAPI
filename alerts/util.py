import datetime

import pytz
from django.db.models import Q, ExpressionWrapper, DurationField, F

from alerts.models import Alert, AlertChannelSend, AlertCommunicationChannelType
from scouting.models import Event, ScoutFieldSchedule, Schedule


def stage_all_field_schedule_alerts():
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

    message += stage_field_schedule_alerts(1, sfss_15, event)
    message += stage_field_schedule_alerts(2, sfss_5, event)
    message += stage_field_schedule_alerts(3, sfss_now, event)

    return message


def stage_field_schedule_alerts(notification, sfss, event):
    message = ''
    for sfs in sfss:
        date_st_utc = sfs.st_time.astimezone(pytz.utc)
        date_end_utc = sfs.end_time.astimezone(pytz.utc)
        date_st_local = date_st_utc.astimezone(pytz.timezone(event.timezone))
        date_end_local = date_end_utc.astimezone(pytz.timezone(event.timezone))
        date_st_str = date_st_local.strftime("%m/%d/%Y, %I:%M%p")
        date_end_str = date_end_local.strftime("%m/%d/%Y, %I:%M%p")

        warning_text = ''
        match notification:
            case 1:
                sfs.notification1 = True
                warning_text = '15 minute warning'
            case 2:
                sfs.notification2 = True
                warning_text = '5 minute warning'
            case 3:
                sfs.notification3 = True
                warning_text = 'time to scout!'

        subject = 'Scouting ' + warning_text
        body = f'You are scheduled to scout from: <@{date_st_str}> to <@{date_end_str}>.\n- PARTs'

        success_txt = 'Stage scouting alert: '
        fail_txt = 'Phone Unable to notify scouting: '
        staged_alerts = []
        try:
            staged_alerts.append(stage_alert(sfs.red_one, subject, body))
            message += success_txt + sfs.red_one.first_name + '\n'
        except Exception as e:
            message += fail_txt + (sfs.red_one.first_name if sfs.red_one is not None else "red one") + '\n'
        try:
            staged_alerts.append(stage_alert(sfs.red_two, subject, body))
            message += success_txt + sfs.red_two.first_name + '\n'
        except Exception as e:
            message += fail_txt + (sfs.red_two.first_name if sfs.red_two is not None else "red two") + '\n'
        try:
            staged_alerts.append(stage_alert(sfs.red_three, subject, body))
            message += success_txt + sfs.red_three.first_name + '\n'
        except Exception as e:
            message += fail_txt + (sfs.red_three.first_name if sfs.red_three is not None else "red three") + '\n'
        try:
            staged_alerts.append(stage_alert(sfs.blue_one, subject, body))
            message += success_txt + sfs.blue_one.first_name + '\n'
        except Exception as e:
            message += fail_txt + (sfs.blue_one.first_name if sfs.blue_one is not None else "blue one") + '\n'
        try:
            staged_alerts.append(stage_alert(sfs.blue_two, subject, body))
            message += success_txt + sfs.blue_two.first_name + '\n'
        except Exception as e:
            message += fail_txt + (sfs.blue_two.first_name if sfs.blue_two is not None else "blue two") + '\n'
        try:
            staged_alerts.append(stage_alert(sfs.blue_three, subject, body))
            message += success_txt + sfs.blue_three.first_name + '\n'
        except Exception as e:
            message += fail_txt + (sfs.blue_three.first_name if sfs.blue_three is not None else "blue three") + '\n'

        for sa in staged_alerts:
            accts = AlertCommunicationChannelType.objects.filter(Q(void_ind='n') & ~Q(alert_comm_typ__in=['message', 'email']))
            for acct in accts:
                stage_alert_channel_send(sa, acct.alert_comm_typ)

        sfs.save()

    return message


def stage_schedule_alerts():
    message = ''
    event = Event.objects.get(Q(current='y') & Q(void_ind='n'))
    curr_time = datetime.datetime.utcnow().astimezone(pytz.timezone(event.timezone))
    schs = Schedule.objects.annotate(
        diff=ExpressionWrapper(F('st_time') - curr_time, output_field=DurationField())) \
        .filter(diff__lte=datetime.timedelta(minutes=6)) \
        .filter(Q(event=event) & Q(notified=False) & Q(void_ind='n')).order_by('sch_typ__sch_typ', 'st_time')

    staged_alerts = []
    for sch in schs:
        date_st_utc = sch.st_time.astimezone(pytz.utc)
        date_end_utc = sch.end_time.astimezone(pytz.utc)
        date_st_local = date_st_utc.astimezone(pytz.timezone(event.timezone))
        date_end_local = date_end_utc.astimezone(pytz.timezone(event.timezone))
        date_st_str = date_st_local.strftime("%m/%d/%Y, %I:%M%p")
        date_end_str = date_end_local.strftime("%m/%d/%Y, %I:%M%p")

        body = f'You are scheduled in the pit from: <@{date_st_str}> to <@{date_end_str}> for <@{sch.sch_typ.sch_nm}>.\n- PARTs'
        staged_alerts.append(stage_alert(sch.user, 'Pit time!', body))
        message += 'Pit Notified: ' + sch.user.first_name + ' : ' + sch.sch_typ.sch_nm + '\n'

    for sa in staged_alerts:
        accts = AlertCommunicationChannelType.objects.filter(Q(void_ind='n') & ~Q(alert_comm_typ__in=['message', 'email']))
        for acct in accts:
            stage_alert_channel_send(sa, acct.alert_comm_typ)

    if message == '':
        message = 'No notifications'

    return message
def stage_alert(user, alert_subject: str, alert_body: str):
    alert = Alert(user=user, alert_subject=alert_subject, alert_body=alert_body)
    alert.save()
    return alert


def stage_alert_channel_send(alert, alert_comm_typ: str):
    acs = AlertChannelSend(
        alert_comm_typ=AlertCommunicationChannelType.objects.get(
            Q(alert_comm_typ=alert_comm_typ) & Q(void_ind='n')),
        alert=alert)
    acs.save()
    return acs
