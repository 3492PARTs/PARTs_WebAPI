import django
from typing import Any

from django.db import transaction
from django.db.models import Q

from alerts.models import Alert, AlertType, ChannelSend, CommunicationChannelType
from general import send_message
from general.security import ret_message
from user.models import User
import user.util


def create_alert(
    u: User,
    alert_subject: str,
    alert_body: str,
    alert_url: str | None = None,
    alert_typ: AlertType | None = None,
) -> Alert:
    """
    Create a new alert for a user.

    Args:
        u: The user to create the alert for
        alert_subject: Subject/title of the alert
        alert_body: Body text of the alert (will be truncated to 4000 characters)
        alert_url: Optional URL associated with the alert
        alert_typ: Optional alert type classification

    Returns:
        The created Alert object
    """
    alert = Alert(
        user=u,
        subject=alert_subject,
        body=alert_body[:4000],
        url=alert_url,
        alert_typ=alert_typ,
    )
    alert.save()
    return alert


def create_channel_send_for_comm_typ(alert: Alert, alert_comm_typ: str) -> ChannelSend:
    """
    Create a channel send record for delivering an alert through a specific communication type.

    Args:
        alert: The alert to be sent
        alert_comm_typ: The communication type code (e.g., 'email', 'discord', 'notification', 'txt')

    Returns:
        The created ChannelSend object
    """
    acs = ChannelSend(
        comm_typ=CommunicationChannelType.objects.get(
            Q(comm_typ=alert_comm_typ) & Q(void_ind="n")
        ),
        alert=alert,
    )
    acs.save()
    return acs


def send_alerts() -> str:
    """
    Process and send all pending alerts that haven't been sent or dismissed.

    This function is typically called by a cron job to process queued alerts.
    It handles different communication channels (email, Discord, webpush, SMS) and
    tracks delivery attempts. Alerts that fail to send will be retried up to 3 times.

    Returns:
        A message string describing which alerts were sent or if there were errors
    """
    message = ""

    # Alert not send, dismissed, and been tried to send 3 or fewer times
    acss = ChannelSend.objects.filter(
        Q(sent_time__isnull=True)
        & Q(dismissed_time__isnull=True)
        & Q(tries__lte=3)
        & Q(void_ind="n")
    )
    for acs in acss:
        success = True
        try:
            match acs.comm_typ.comm_typ:
                case "email":
                    url = f"\n{acs.alert.url}" if acs.alert.url is not None else ""
                    send_message.send_email(
                        acs.alert.user.email,
                        acs.alert.subject,
                        "generic_email",
                        {
                            "message": f"{acs.alert.body}{url}",
                            "user": acs.alert.user,
                        },
                    )
                    message += "Email"
                case "message":
                    # this is because I have not decided what to do yet
                    message += "message not configured"
                case "notification":
                    message += send_message.send_webpush(
                        acs.alert.user,
                        acs.alert.subject,
                        acs.alert.body,
                        acs.alert.id,
                    )
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

                    # this is the system user id
                    if acs.alert.user.id == -1:
                        u = "@Student"

                    discord_message = f"{acs.alert.subject}:\n {u}\n {acs.alert.body}"
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
            alert = f"An error occurred while sending alert: {acs.alert.user.get_full_name()}  acs id: {acs.id}"
            message += alert + "\n"
            ret_message(alert, True, "alerts.util.send_alerts", 0, e)
        if not success:
            acs.tries = acs.tries + 1
            acs.save()
    if message == "":
        message = "NONE TO SEND"

    return message


def get_user_alerts(user_id: str, comm_typ_cd: str) -> list[dict[str, Any]]:
    """
    Get all undismissed alerts for a user on a specific communication channel.

    Args:
        user_id: The ID of the user
        comm_typ_cd: The communication type code to filter by

    Returns:
        List of dictionaries containing alert information (id, subject, body, url, staged_time, etc.)
    """
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
                "url": a.alert.url,
                "staged_time": a.alert.staged_time,
            }
        )
    return notifs


def dismiss_alert(channel_send_id: str) -> None:
    """
    Mark a channel send as dismissed by the user.

    Args:
        channel_send_id: The ID of the ChannelSend record to dismiss
    """
    acs = ChannelSend.objects.get(
        Q(dismissed_time__isnull=True)
        & Q(void_ind="n")
        & Q(id=channel_send_id)
        & Q(alert__void_ind="n")
    )

    acs.dismissed_time = django.utils.timezone.now()
    acs.save()


def send_alerts_to_role(
    subject: str,
    body: str,
    alert_role: str,
    channels: list[str],
    ignore_user_id: int | None = None,
    url: str | None = None,
    alert_type: AlertType | None = None,
) -> list[Alert]:
    """
    Create and queue alerts for all users with a specific role/permission.

    Args:
        subject: Alert subject line
        body: Alert body text
        alert_role: The permission/role codename to target
        channels: List of communication channel types to send through (e.g., ['email', 'discord'])
        ignore_user_id: Optional user ID to exclude from receiving the alert
        url: Optional URL to include in the alert
        alert_type: Optional AlertType classification

    Returns:
        List of created Alert objects
    """
    with transaction.atomic():
        alerts = []
        users = user.util.get_users_with_permission(alert_role)
        for u in users:
            if ignore_user_id is not None and u.id == ignore_user_id:
                continue
            else:
                alerts.append(
                    create_alert(u, subject, body, alert_url=url, alert_typ=alert_type)
                )

        for a in alerts:
            for acct in channels:
                create_channel_send_for_comm_typ(a, acct)

        return alerts


def get_alert_type(alert_typ: str) -> AlertType:
    """
    Retrieve an AlertType by its type code.

    Args:
        alert_typ: The alert type code to look up

    Returns:
        The AlertType object with the specified code
    """
    return AlertType.objects.get(Q(alert_typ=alert_typ) & Q(void_ind="n"))
