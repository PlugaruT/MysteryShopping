import logging
from smtplib import SMTPRecipientsRefused

from django.core.mail import get_connection
from django.core.mail.message import EmailMultiAlternatives
from django.template.loader import get_template

log = logging.getLogger(__name__)


class DetractorEmailDispatcher:
    def __init__(self, recipients):
        if isinstance(recipients, str):
            recipients = [recipients]
        self.recipients = recipients

    def send_new_detractor_email(self):
        subject_line = 'New detractor in the --place name--'

        context = {
            'random': 'random'
        }

        text_content = self.get_content_for_template('detractors/new_detractor.txt', context)
        html_content = self.get_content_for_template('detractors/new_detractor.html', context)

        email = EmailMultiAlternatives(subject=subject_line, body=text_content, to=self.recipients)
        email.attach_alternative(html_content, 'text/html')

        with get_connection() as connection:
            if not self._send_email(connection, email):
                return False

        return True

    def send_new_detractor_case_email(self):
        subject_line = 'asdasd'
        context = {
            "random": "random"
        }

        text_content = self.get_content_for_template('detractors/new_detractor_case.txt', context)
        html_content = self.get_content_for_template('detractors/new_detractor_case.html', context)

        email = EmailMultiAlternatives(subject=subject_line, body=text_content, to=self.recipients)
        email.attach_alternative(html_content, 'text/html')

        with get_connection() as connection:
            if not self._send_email(connection, email):
                return False

        return True

    @staticmethod
    def _send_email(connection, email):
        try:
            return connection.send_messages([email])
        except SMTPRecipientsRefused:
            log.error('Could not send email to {}'.format(email.to))

    @staticmethod
    def get_content_for_template(template_path, context):
        text_template = get_template(template_path)
        return text_template.render(context)
