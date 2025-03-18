import datetime

import pytz
import requests
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.conf import settings
from webpush import send_user_notification
from pywebpush import WebPushException

import general


def send_email(to_email: str, subject: str, template: str, cntx: dict):
    plaintext = get_template("./email_templates/" + template + ".txt")
    html = get_template("email_templates/" + template + ".html")

    text_content = plaintext.render(cntx)
    html_content = html.render(cntx)

    email = EmailMultiAlternatives(
        subject, text_content, "team3492@gmail.com", [to_email]
    )
    email.attach_alternative(html_content, "text/html")
    email.send()


def send_discord_notification(message: str):
    url = settings.DISCORD_NOTIFICATION_WEBHOOK
    myobj = {"content": message}

    x = requests.post(url, json=myobj)
    if not x.ok:
        raise Exception("discord sending issue")


def send_webpush(user, subject: str, body: str, alert_id: int):
    payload = {
        "notification": {
            "title": subject,
            "body": body,
            "icon": "assets/icons/icon-128x128.png",
            "badge": "badge",
            "tag": alert_id,
            "requireInteraction": True,
            "silent": False,
            "vibrate": [200, 100, 200],
            "timestamp": datetime.datetime.utcnow()
            .replace(tzinfo=pytz.utc)
            .isoformat(),
            "data": {  # i believe this can be anything
                "dateOfArrival": datetime.datetime.utcnow()
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

    msg = "Successfully Webpush."
    try:
        send_user_notification(user=user, payload=payload, ttl=1000)
    except WebPushException as e:
        msg = "An error occurred while sending Webpush."
        general.ret_message(
            msg,
            True,
            "send_webpush",
            -1,
            e,
        )

    return msg
