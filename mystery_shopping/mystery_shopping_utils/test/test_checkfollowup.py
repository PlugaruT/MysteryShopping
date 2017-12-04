from django.core import mail
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from mystery_shopping.factories.respondents import RespondentCaseFactory
from mystery_shopping.factories.users import UserFactory


class CheckFollowupTest(TestCase):
    def setUp(self):
        self.user = UserFactory()

    def test_command_when_there_are_no_cases(self):
        call_command('checkfollowup')

        self.assertEqual(0, len(mail.outbox))

    def test_command_when_one_email_should_be_sent(self):
        RespondentCaseFactory(follow_up_user=self.user, follow_up_date=timezone.now())

        call_command('checkfollowup')

        self.assertEqual(1, len(mail.outbox))
        self.assertIn(self.user.email, mail.outbox[0].to)

    def test_command_when_more_emails_should_be_sent(self):
        RespondentCaseFactory(follow_up_user=self.user, follow_up_date=timezone.now())
        RespondentCaseFactory(follow_up_user=self.user, follow_up_date=timezone.now())
        RespondentCaseFactory(follow_up_user=self.user, follow_up_date=timezone.now())
        RespondentCaseFactory(follow_up_user=self.user)
        RespondentCaseFactory(follow_up_user=self.user)

        call_command('checkfollowup')

        self.assertEqual(3, len(mail.outbox))
        for email in mail.outbox:
            self.assertEqual([self.user.email], email.to)
