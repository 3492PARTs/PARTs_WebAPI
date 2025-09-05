import datetime
import pytz
from django.db.models import Q, ExpressionWrapper, DurationField, F
from django.utils import timezone
from django.conf import settings

from form.models import FormType, Response
import scouting.util
from alerts.util import (
    create_alert,
    create_channel_send_for_comm_typ,
    send_alerts_to_role,
)
import user
from admin.models import ErrorLog
from alerts.models import AlertType
from scouting.models import FieldSchedule, Schedule


def stage_alerts():
    ret = "all field alerts\n"
    ret += stage_all_field_schedule_alerts()
    ret += "schedule alerts\n"
    ret += stage_schedule_alerts()
    ret += "Error alerts\n"
    ret += stage_error_alerts()
    ret += "Contact Form alerts\n"
    ret += stage_form_alerts("team-cntct")
    ret += "Application Form alerts\n"
    ret += stage_form_alerts("team-app")
    return ret


def stage_error_alerts():
    message = ""

    alert_typ = AlertType.objects.get(alert_typ="error")

    errors = ErrorLog.objects.filter(Q(time__gte=alert_typ.last_run) & Q(void_ind="n"))
    for error in errors:
        message += f"{error}\n\n"

    if message == "":
        message = "No notifications"
    else:
        send_alerts_to_role(
            alert_typ.subject,
            f"{alert_typ.body}\n\n{message}",
            "error_alert",
            ["email", "notification"],
        )

    alert_typ.last_run = timezone.now()
    alert_typ.save()

    return message


def stage_form_alerts(form_type: str):
    message = ""

    alert_typ = AlertType.objects.get(alert_typ=form_type)
    form_type = FormType.objects.get(form_typ=form_type)

    responses = Response.objects.filter(
        Q(form_typ=form_type) & Q(time__gte=alert_typ.last_run) & Q(void_ind="n")
    )

    for response in responses:
        url = f'{settings.FRONTEND_ADDRESS}{"contact" if form_type.form_typ == "team-cntct" else "join/team-application"}?response_id={response.id}'
        message += f"{alert_typ.subject} ID: {response.id}\n"
        send_alerts_to_role(
            alert_typ.subject,
            alert_typ.body,
            "form_alert",
            ["email", "notification"],
            url=url,
        )

    if message == "":
        message = "No notifications"

    alert_typ.last_run = timezone.now()
    alert_typ.save()

    return message


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
            staged_alerts.append(create_alert(sfs.red_one, subject, body))
            message += success_txt + sfs.red_one.get_full_name() + "\n"

        if sfs.red_two is not None:
            staged_alerts.append(create_alert(sfs.red_two, subject, body))
            message += success_txt + sfs.red_two.get_full_name() + "\n"

        if sfs.red_three is not None:
            staged_alerts.append(create_alert(sfs.red_three, subject, body))
            message += success_txt + sfs.red_three.get_full_name() + "\n"

        if sfs.blue_one is not None:
            staged_alerts.append(create_alert(sfs.blue_one, subject, body))
            message += success_txt + sfs.blue_one.get_full_name() + "\n"

        if sfs.blue_two is not None:
            staged_alerts.append(create_alert(sfs.blue_two, subject, body))
            message += success_txt + sfs.blue_two.get_full_name() + "\n"

        if sfs.blue_three is not None:
            staged_alerts.append(create_alert(sfs.blue_three, subject, body))
            message += success_txt + sfs.blue_three.get_full_name() + "\n"

        for sa in staged_alerts:
            for acct in ["txt", "notification", "discord"]:
                create_channel_send_for_comm_typ(sa, acct)

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

    alert = create_alert(sch.user, "Pit time!", body)
    for acct in ["txt", "notification", "discord"]:
        create_channel_send_for_comm_typ(alert, acct)

    return (
        "Pit Notified: " + sch.user.get_full_name() + " : " + sch.sch_typ.sch_nm + "\n"
    )


def stage_scout_admin_alerts(subject: str, body: str):
    staged_alerts = []
    users = user.util.get_users_with_permission("scoutadmin")
    for u in users:
        staged_alerts.append(create_alert(u, subject, body))

    return staged_alerts
