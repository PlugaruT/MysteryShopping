from django.test import TestCase
from mystery_shopping.mail_service.mail import DetractorEmailDispatcher


class TestDetractorEmailDispatcher(TestCase):
    def setUp(self):
        self.DEFAULT_FROM_EMAIL = 'test@sparklabs.md'

    def test_init_with_one_recipient(self):
        to_email = 'user@email.com'

        service = DetractorEmailDispatcher(to_email)

        self.assertListEqual(service.recipients, [to_email])

    def test_init_with_more_recipients(self):
        to_emails = ['user@email.com', 'user2@email.com']

        service = DetractorEmailDispatcher(to_emails)

        self.assertListEqual(service.recipients, to_emails)

    def test_send_new_detractor_email(self):
        pass

    def test_send_new_detractors_case_email(self):
        pass
