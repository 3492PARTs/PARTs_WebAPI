import requests
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.conf import settings


def send_email(to_email: str, subject: str, template: str, cntx: dict):
    plaintext = get_template('./email_templates/' + template + '.txt')
    html = get_template('email_templates/' + template + '.html')

    text_content = plaintext.render(cntx)
    html_content = html.render(cntx)

    email = EmailMultiAlternatives(
        subject, text_content, 'team3492@gmail.com', [to_email])
    email.attach_alternative(html_content, "text/html")
    email.send()


def send_discord_notification(message: str):
    url = settings.DISCORD_NOTIFICATION_WEBHOOK
    myobj = {'content': message}

    x = requests.post(url, json=myobj)
    if not x.ok:
        raise Exception('discord sending issue')
