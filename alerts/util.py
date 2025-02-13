import datetime
import django

import pytz
from django.db.models import Q, ExpressionWrapper, DurationField, F
from django.utils import timezone

import scouting.util
from alerts.models import Alert, ChannelSend, CommunicationChannelType
from general import send_message
from general.security import ret_message
from scouting.models import Event, FieldSchedule, Schedule
from user.models import User
import user.util


def stage_all_field_schedule_alerts():
    message = ""
    event = scouting.util.get_current_event()
    curr_time = timezone.now()

    sfss_15 = (
        FieldSchedule.objects.annotate(
            diff=ExpressionWrapper(
                F("st_time") - curr_time, output_field=DurationField()
            )
        )
        .filter(diff__lte=datetime.timedelta(minutes=15.5))
        .filter(Q(event=event) & Q(notification1=False) & Q(void_ind="n"))
    )

    sfss_5 = (
        FieldSchedule.objects.annotate(
            diff=ExpressionWrapper(
                F("st_time") - curr_time, output_field=DurationField()
            )
        )
        .filter(diff__lte=datetime.timedelta(minutes=5.5))
        .filter(Q(event=event) & Q(notification2=False) & Q(void_ind="n"))
    )

    sfss_now = (
        FieldSchedule.objects.annotate(
            diff=ExpressionWrapper(
                F("st_time") - curr_time, output_field=DurationField()
            )
        )
        .filter(diff__lt=datetime.timedelta(minutes=0.5))
        .filter(Q(event=event) & Q(notification3=False) & Q(void_ind="n"))
    )

    message += stage_field_schedule_alerts(1, sfss_15)
    message += stage_field_schedule_alerts(2, sfss_5)
    message += stage_field_schedule_alerts(3, sfss_now)

    """
    sfss_missing_scouts = ScoutFieldSchedule.objects \
        .annotate(diff=ExpressionWrapper(curr_time - F('st_time'), output_field=DurationField())) \
        .filter(diff__gte=datetime.timedelta(minutes=4.5)) \
        .filter(Q(event=event) & Q(void_ind='n')) \
        .filter(Q(red_one_check_in__isnull=True) | Q(red_two_check_in__isnull=True) |
                Q(red_three_check_in__isnull=True) | Q(blue_one_check_in__isnull=True) |
                Q(blue_two_check_in__isnull=True) | Q(blue_three_check_in__isnull=True))

    for sfs_missing_scouts in sfss_missing_scouts:
        date_st_utc = sfs_missing_scouts.st_time.astimezone(pytz.utc)
        date_end_utc = sfs_missing_scouts.end_time.astimezone(pytz.utc)
        date_st_local = date_st_utc.astimezone(pytz.timezone(sfs_missing_scouts.event.timezone))
        date_end_local = date_end_utc.astimezone(pytz.timezone(sfs_missing_scouts.event.timezone))
        date_st_str = date_st_local.strftime("%m/%d/%Y, %I:%M%p")
        date_end_str = date_end_local.strftime("%m/%d/%Y, %I:%M%p")

        subject = 'Late for Scouting!!!'
        body = f'You are scheduled to scout from: {date_st_str} to {date_end_str}.\n- PARTs'

        lead_scout_subject = 'You have a late scout'
        lead_scout_body = f' is late, they are scheduled from: {date_st_str} to {date_end_str}.'

        success_txt = 'Stage past due scouting alert: '
        # fail_txt = 'Unable to stage scouting alert: '
        staged_alerts = []

        if (sfs_missing_scouts.red_one is not None and sfs_missing_scouts.red_one_check_in is None and not
                has_access(sfs_missing_scouts.red_one.id, 'scoutadmin')):
            staged_alerts.append(stage_alert(sfs_missing_scouts.red_one, subject, body))
            staged_alerts.extend(stage_scout_admin_alerts(lead_scout_subject,
                                                          sfs_missing_scouts.red_one.get_full_name() + lead_scout_body))
            message += success_txt + sfs_missing_scouts.red_one.get_full_name() + '\n'

        if (sfs_missing_scouts.red_two is not None and sfs_missing_scouts.red_two_check_in is None and not
                has_access(sfs_missing_scouts.red_two.id, 'scoutadmin')):
            staged_alerts.append(stage_alert(sfs_missing_scouts.red_two, subject, body))
            staged_alerts.extend(stage_scout_admin_alerts(lead_scout_subject,
                                                          sfs_missing_scouts.red_two.get_full_name() + lead_scout_body))
            message += success_txt + sfs_missing_scouts.red_two.get_full_name() + '\n'

        if (sfs_missing_scouts.red_three is not None and sfs_missing_scouts.red_three_check_in is None and not
                has_access(sfs_missing_scouts.red_three.id, 'scoutadmin')):
            staged_alerts.append(stage_alert(sfs_missing_scouts.red_three, subject, body))
            staged_alerts.extend(stage_scout_admin_alerts(lead_scout_subject,
                                                          sfs_missing_scouts.red_three.get_full_name() +
                                                          lead_scout_body))
            message += success_txt + sfs_missing_scouts.red_three.get_full_name() + '\n'

        if (sfs_missing_scouts.blue_one is not None and sfs_missing_scouts.blue_one_check_in is None and not
                has_access(sfs_missing_scouts.blue_one.id, 'scoutadmin')):
            staged_alerts.append(stage_alert(sfs_missing_scouts.blue_one, subject, body))
            staged_alerts.extend(stage_scout_admin_alerts(lead_scout_subject,
                                                          sfs_missing_scouts.blue_one.get_full_name() +
                                                          lead_scout_body))
            message += success_txt + sfs_missing_scouts.blue_one.get_full_name() + '\n'

        if (sfs_missing_scouts.blue_two is not None and sfs_missing_scouts.blue_two_check_in is None and not
                has_access(sfs_missing_scouts.blue_two.id, 'scoutadmin')):
            staged_alerts.append(stage_alert(sfs_missing_scouts.blue_two, subject, body))
            staged_alerts.extend(stage_scout_admin_alerts(lead_scout_subject,
                                                          sfs_missing_scouts.blue_two.get_full_name() +
                                                          lead_scout_body))
            message += success_txt + sfs_missing_scouts.blue_two.get_full_name() + '\n'

        if (sfs_missing_scouts.blue_three is not None and sfs_missing_scouts.blue_three_check_in is None and not
                has_access(sfs_missing_scouts.blue_three.id, 'scoutadmin')):
            staged_alerts.append(stage_alert(sfs_missing_scouts.blue_three, subject, body))
            staged_alerts.extend(stage_scout_admin_alerts(lead_scout_subject,
                                                          sfs_missing_scouts.blue_three.get_full_name() +
                                                          lead_scout_body))
            message += success_txt + sfs_missing_scouts.blue_three.get_full_name() + '\n'

        for sa in staged_alerts:
            for acct in ['txt', 'notification']:
                stage_alert_channel_send(sa, acct)
    """
    if message == "":
        message = "No notifications"

    return message


def stage_field_schedule_alerts(notification, sfss):
    message = ""
    for sfs in sfss:
        date_st_utc = sfs.st_time.astimezone(pytz.utc)
        date_end_utc = sfs.end_time.astimezone(pytz.utc)
        date_st_local = date_st_utc.astimezone(pytz.timezone(sfs.event.timezone))
        date_end_local = date_end_utc.astimezone(pytz.timezone(sfs.event.timezone))
        date_st_str = date_st_local.strftime("%m/%d/%Y, %I:%M%p")
        date_end_str = date_end_local.strftime("%m/%d/%Y, %I:%M%p")

        match notification:
            case 1:
                sfs.notification1 = True
                warning_text = "15 minute warning"
            case 2:
                sfs.notification2 = True
                warning_text = "5 minute warning"
            case 3:
                sfs.notification3 = True
                warning_text = "time to scout!"
            case _:
                warning_text = "time to scout!"

        subject = "Scouting " + warning_text
        body = f"You are scheduled to scout from: {date_st_str} to {date_end_str}.\n- PARTs"

        success_txt = "Stage scouting alert: "
        # fail_txt = 'Unable to stage scouting alert: '
        staged_alerts = []
        if sfs.red_one is not None:
            staged_alerts.append(stage_alert(sfs.red_one, subject, body))
            message += success_txt + sfs.red_one.get_full_name() + "\n"

        if sfs.red_two is not None:
            staged_alerts.append(stage_alert(sfs.red_two, subject, body))
            message += success_txt + sfs.red_two.get_full_name() + "\n"

        if sfs.red_three is not None:
            staged_alerts.append(stage_alert(sfs.red_three, subject, body))
            message += success_txt + sfs.red_three.get_full_name() + "\n"

        if sfs.blue_one is not None:
            staged_alerts.append(stage_alert(sfs.blue_one, subject, body))
            message += success_txt + sfs.blue_one.get_full_name() + "\n"

        if sfs.blue_two is not None:
            staged_alerts.append(stage_alert(sfs.blue_two, subject, body))
            message += success_txt + sfs.blue_two.get_full_name() + "\n"

        if sfs.blue_three is not None:
            staged_alerts.append(stage_alert(sfs.blue_three, subject, body))
            message += success_txt + sfs.blue_three.get_full_name() + "\n"

        for sa in staged_alerts:
            for acct in ["txt", "notification", "discord"]:
                stage_channel_send_for_all_channels(sa, acct)

        sfs.save()

    return message


def stage_schedule_alerts():
    message = ""
    event = scouting.util.get_current_event()
    curr_time = timezone.now()  # .astimezone(pytz.timezone(event.timezone))
    schs = (
        Schedule.objects.annotate(
            diff=ExpressionWrapper(
                F("st_time") - curr_time, output_field=DurationField()
            )
        )
        .filter(diff__lte=datetime.timedelta(minutes=6))
        .filter(Q(event=event) & Q(notified=False) & Q(void_ind="n"))
        .order_by("sch_typ__sch_typ", "st_time")
    )

    for sch in schs:
        message += stage_schedule_alert(sch)
        sch.notified = True
        sch.save()

    if message == "":
        message = "No notifications"

    return message


def stage_schedule_alert(sch: Schedule):
    date_st_utc = sch.st_time.astimezone(pytz.utc)
    date_end_utc = sch.end_time.astimezone(pytz.utc)
    date_st_local = date_st_utc.astimezone(pytz.timezone(sch.event.timezone))
    date_end_local = date_end_utc.astimezone(pytz.timezone(sch.event.timezone))
    date_st_str = date_st_local.strftime("%m/%d/%Y, %I:%M%p")
    date_end_str = date_end_local.strftime("%m/%d/%Y, %I:%M%p")

    body = f"You are scheduled in the pit from: {date_st_str} to {date_end_str} for {sch.sch_typ.sch_nm}.\n- PARTs"

    alert = stage_alert(sch.user, "Pit time!", body)
    for acct in ["txt", "notification", "discord"]:
        stage_channel_send_for_all_channels(alert, acct)

    return (
        "Pit Notified: " + sch.user.get_full_name() + " : " + sch.sch_typ.sch_nm + "\n"
    )


def stage_scout_admin_alerts(subject: str, body: str):
    staged_alerts = []
    users = user.util.get_users_with_permission("scoutadmin")
    for u in users:
        staged_alerts.append(stage_alert(u, subject, body))

    return staged_alerts


def stage_alert(u: User, alert_subject: str, alert_body: str):
    alert = Alert(user=u, subject=alert_subject, body=alert_body)
    alert.save()
    return alert


def stage_channel_send_for_all_channels(alert: Alert, alert_comm_typ: str):
    acs = ChannelSend(
        comm_typ=CommunicationChannelType.objects.get(
            Q(comm_typ=alert_comm_typ) & Q(void_ind="n")
        ),
        alert=alert,
    )
    acs.save()
    return acs


def send_alerts():
    message = "send alerts\n"

    # Alert not send, dismissed, and been tried to send 3 or fewer times
    acss = ChannelSend.objects.filter(
        Q(sent_time__isnull=True) & Q(dismissed_time__isnull=True) & Q(tries__lte=3) & Q(void_ind="n")
    )
    for acs in acss:
        success = True
        try:
            match acs.comm_typ.comm_typ:
                case "email":
                    send_message.send_email(
                        acs.alert.user.email,
                        acs.alert.subject,
                        "generic_email",
                        {"message": acs.alert.body, "user": acs.alert.user},
                    )
                    message += "Email"
                case "message":
                    # this is because I have not decided what to do yet
                    message += "message not configured"
                case "notification":
                    send_message.send_webpush(
                        acs.alert.user,
                        acs.alert.subject,
                        acs.alert.body,
                        acs.alert.id,
                    )
                    message += "Webpush"
                case "txt":
                    if (
                        acs.alert.user.phone is not None
                        and acs.alert.user.phone_type is not None
                    ):
                        send_message.send_email(
                            acs.alert.user.phone + acs.alert.user.phone_type.phone_type,
                            acs.alert.subject,
                            "generic_text",
                            {"message": acs.alert.body},
                        )
                        message += "Phone"
                    else:
                        message += "Phone FAILED"
                        success = False
                case "discord":
                    u = (
                        f"<@{acs.alert.user.discord_user_id}>"
                        if acs.alert.user.discord_user_id
                        else acs.alert.user.get_full_name()
                    )
                    discord_message = (
                        f"{acs.alert.subject}:\n {u}\n {acs.alert.body}"
                    )
                    send_message.send_discord_notification(discord_message)
                    message += "Discord"

            if success:
                acs.sent_time = django.utils.timezone.now()
                acs.save()
            message += (
                " Notified: "
                + acs.alert.user.get_full_name()
                + " acs id: "
                + str(acs.id)
                + "\n"
            )
        except Exception as e:
            success = False
            alert =  f"An error occurred while sending alert: {acs.alert.user.get_full_name()}  acs id: {acs.id}"
            message += alert + "\n"
            return ret_message(alert, True, "alerts.util.send_alerts", 0, e)
        if not success:
            acs.tries = acs.tries + 1
            acs.save()
    if message == "":
        message = "No notifications"

    return message


def get_user_alerts(user_id: str, comm_typ_cd: str):
    acs = ChannelSend.objects.filter(
        Q(dismissed_time__isnull=True)
        & Q(comm_typ_id=comm_typ_cd)
        & Q(void_ind="n")
        & Q(alert__user_id=user_id)
        & Q(alert__void_ind="n")
    ).select_related("alert")

    notifs = []
    for a in acs:
        notifs.append(
            {
                "id": a.alert.id,
                "channel_send_id": a.id,
                "subject": a.alert.subject,
                "body": a.alert.body,
                "staged_time": a.alert.staged_time,
            }
        )
    return notifs


def dismiss_alert(channel_send_id: str):
    acs = ChannelSend.objects.get(
        Q(dismissed_time__isnull=True)
        & Q(void_ind="n")
        & Q(id=channel_send_id)
        & Q(alert__void_ind="n")
    )

    acs.dismissed_time = django.utils.timezone.now()
    acs.save()


def stage_alerts():
    ret = "all field alerts\n"
    ret += stage_all_field_schedule_alerts()
    ret += "schedule alerts\n"
    ret += stage_schedule_alerts()
    return ret


def send_alerts_to_role(subject: str, body: str, alert_role: str, channels: [], user_id: int=None):
    alerts = []
    users = user.util.get_users_with_permission(alert_role)
    for u in users:
        if user_id is not None and u.id == user_id:
            continue
        else:
            alerts.append(stage_alert(u, subject, body))

    for a in alerts:
        for acct in channels:
            stage_channel_send_for_all_channels(
                a, acct
            )