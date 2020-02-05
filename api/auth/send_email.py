from django.core.mail import EmailMessage
from django.template.loader import render_to_string


def send_message(user_email, subject, template, data):
    message = render_to_string('email_templates/' + template, data)
    email = EmailMessage(
        subject, message, to=[user_email]
    )
    email.send()
