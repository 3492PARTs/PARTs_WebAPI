from datetime import datetime, timezone

from json import dumps

import pytz
import requests
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.conf import settings
from webpush import send_user_notification
from pywebpush import WebPushException

from general.security import ret_message


def send_email(to_email: str | list[str], subject: str, template: str, cntx: dict):
    plaintext = get_template("./email_templates/" + template + ".txt")
    html = get_template("email_templates/" + template + ".html")

    text_content = plaintext.render(cntx)
    html_content = html.render(cntx)

    subject = add_test_env_subject(subject)

    email = EmailMultiAlternatives(
        subject,
        text_content,
        "team3492@gmail.com",
        [to_email] if not isinstance(to_email, list) else to_email,
    )
    email.attach_alternative(html_content, "text/html")
    email.send()


def send_discord_notification(message: str):
    url = settings.DISCORD_NOTIFICATION_WEBHOOK

    message = add_test_env_subject(message)

    myobj = {"content": message}

    x = requests.post(url, json=myobj)
    if not x.ok:
        raise Exception("discord sending issue")


def send_webpush(user, subject: str, body: str, alert_id: int):
    subject = add_test_env_subject(subject)

    payload = {
        "notification": {
            "title": subject,
            "body": body[0:3500],  # max length is 4096 bytes
            "icon": "assets/icons/icon-128x128.png",
            "badge": "badge",
            "tag": alert_id,
            "requireInteraction": True,
            "silent": False,
            "vibrate": [200, 100, 200],
            "timestamp": datetime.now(timezone.utc)
            .replace(tzinfo=pytz.utc)
            .isoformat(),
            "data": {  # i believe this can be anything
                "dateOfArrival": datetime.now(timezone.utc)
                .replace(tzinfo=pytz.utc)
                .isoformat(),
                "primaryKey": 1,
            },
            "actions": [
                {"action": "explore", "title": "Go to the site"},
                {"action": "field-scouting", "title": "Go to scouting", "icon": "icon"},
            ],
        }
    }

    msg = "Successfully sent Webpush."
    try:
        send_user_notification(user=user, payload=payload, ttl=1000)
    except WebPushException as e:
        json_string = dumps(payload)
        json_bytes = json_string.encode("utf-8")
        payload_bytes = len(json_bytes)

        msg = f"An error occurred while sending Webpush.\nBytes: {payload_bytes}"
        ret_message(msg, True, "send_webpush", -1, e, f"Payload:\n{json_string}")

    return msg


def add_test_env_subject(subject: str):
    if settings.ENVIRONMENT != "main":
        return f"TEST ENVIRONMENT - {settings.ENVIRONMENT}: {subject}"
    return subject
