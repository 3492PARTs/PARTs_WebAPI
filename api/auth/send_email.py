from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template


def send_message(to_email: str, subject: str, template: str, cntx: dict):
    plaintext = get_template('email_templates/' + template + '.txt')
    html = get_template('email_templates/' + template + '.html')

    text_content = plaintext.render(cntx)
    html_content = html.render(cntx)

    email = EmailMultiAlternatives(subject, text_content, 'team3492@gmail.com', [to_email])
    email.attach_alternative(html_content, "text/html")
    email.send()
