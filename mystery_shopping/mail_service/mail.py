import logging
from smtplib import SMTPRecipientsRefused
from django.template.loader import get_template
from django.core.mail import get_connection
from django.core.mail.message import EmailMultiAlternatives

log = logging.getLogger(__name__)


class EmailDispatcher:
    def __init__(self, recipients, text_content, html_content, subject):
        if isinstance(recipients, str):
            recipients = [recipients]
        self.recipients = recipients
        self.text_content = text_content
        self.html_content = html_content
        self.subject = subject

    def build_and_send(self):
        email = EmailMultiAlternatives(subject=self.subject, body=self.text_content, to=self.recipients)
        email.attach_alternative(self.html_content, 'text/html')

        with get_connection() as connection:
            if not self._send_email(connection, email):
                return False

    @staticmethod
    def _send_email(connection, email):
        try:
            return connection.send_messages([email])
        except SMTPRecipientsRefused:
            log.error('Could not send email to {}'.format(email.to))
            return False


def get_text_and_html_content(template_path, context):
    """
    Method that returns the contents of a template in plain text and html
    :param template_path: string of the form 'folder_name/template_name', without file extension
    :param context: dict that contains values that should be passed to the template
    :return: tuple with text content and html content of the template
    """
    text_content = get_content_for_template('{}.txt'.format(template_path), context)
    html_content = get_content_for_template('{}.html'.format(template_path), context)
    return text_content, html_content


def get_content_for_template(template_path, context):
    """
    Method that returns the template with the values from context
    :param template_path: string of the form 'folder_name/template_name.html', should contain the file extenstion
    :param context: dict that contains values that should be passed to the template
    :return: rendered template with passed context
    """

    text_template = get_template(template_path)
    return text_template.render(context)
