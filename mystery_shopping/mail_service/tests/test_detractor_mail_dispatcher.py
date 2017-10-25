from django.test import TestCase

from mystery_shopping.mail_service.mail import EmailDispatcher


class TestDetractorEmailDispatcher(TestCase):
    def setUp(self):
        self.DEFAULT_FROM_EMAIL = 'test@sparklabs.md'

    def test_init_with_one_recipient_as_str(self):
        to_email = 'user@email.com'

        service = EmailDispatcher(to_email, None, None, None)

        self.assertListEqual(service.recipients, [to_email])

    def test_init_with_one_recipient_as_list(self):
        to_email = ['user@email.com']

        service = EmailDispatcher(to_email, None, None, None)

        self.assertListEqual(service.recipients, to_email)

    def test_init_with_more_recipients_as_list(self):
        to_emails = ['user@email.com', 'user2@email.com']

        service = EmailDispatcher(to_emails, None, None, None)

        self.assertListEqual(service.recipients, to_emails)
