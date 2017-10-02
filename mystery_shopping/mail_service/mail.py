import logging
from collections import Sequence
from smtplib import SMTPRecipientsRefused

from django.core.mail import get_connection
from django.core.mail.backends.smtp import EmailBackend
from django.core.mail.message import EmailMultiAlternatives
from django.template.loader import get_template

log = logging.getLogger(__name__)


class DetractorMailDispatcher:
    def __init__(self, recipients):
        if not isinstance(recipients, Sequence):
            recipients = [recipients]

        self.recipients = recipients

    def send_new_detractor_email(self):
        subject_line = 'New detractor in the --place name--'

        context = {
            'random': 'random'
        }

        text_content = self.get_content_for_template(
            'new_detractor.txt', context)
        html_content = self.get_content_for_template(
            'hew_detractor.html', context)

        email = EmailMultiAlternatives(subject=subject_line,
                                       body=text_content,
                                       to=self.recipients)
        email.attach_alternative(html_content, 'text/html')

        with get_connection() as connection:
            if not self.send_email(connection, email)
                return False

        return True

    def send_new_detractor_case_email(self):
        subject_line = 'asdasd'
        context = {
            "random": "random"
        }

           text_content = self.get_content_for_template(
            'new_detractor.txt', context)
        html_content = self.get_content_for_template(
            'hew_detractor.html', context)

        email = EmailMultiAlternatives(subject=subject_line,
                                       body=text_content,
                                       to=self.recipients)
        email.attach_alternative(html_content, 'text/html')

        with get_connection() as connection:
            if not self.send_email(connection, email)
                return False

        return True

    def send_email(self, connection, email)
        try:
            return connection.send_message([email])
        except SMTPRecipientsRefused:
            log.error('Could not send email to {}'.format(email.to))

    @staticmethod
    def get_content_for_template(template_name, context)
        text_template = get_template('detractors/{}'.format(template_name))
        return text_template.render(context)
