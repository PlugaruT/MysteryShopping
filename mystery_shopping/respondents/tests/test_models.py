from django.test import TestCase
from django_fsm_log.models import StateLog

from mystery_shopping.factories.respondents import RespondentCaseFactory
from mystery_shopping.factories.users import UserFactory
from mystery_shopping.respondents.models import RespondentCase


class DetractorCase(TestCase):
    def test_that_case_is_created_assigned(self):
        case = RespondentCaseFactory()

        self.assertEqual(case.state, RespondentCase.STATE.ASSIGNED)

    def test_case_escalation(self):
        case = RespondentCaseFactory()

        case.escalate('reason')
        case.save()

        self.assertEqual(case.state, RespondentCase.STATE.ESCALATED)
        self.assertEqual(case.comments.count(), 1)
        comment = case.comments.all()[0]
        self.assertEqual(comment.text, 'reason')

    def test_case_assignment(self):
        case = RespondentCaseFactory(state=RespondentCase.STATE.ESCALATED)
        to_user = UserFactory()
        manager = UserFactory()

        case.assign(to=to_user, comment='reason', user=manager)

        self.assertEqual(case.state, RespondentCase.STATE.ASSIGNED)
        self.assertEqual(case.comments.count(), 1)
        comment = case.comments.all()[0]
        self.assertEqual(comment.text, 'reason')

        logs = StateLog.objects.for_(case).all()
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0].state, RespondentCase.STATE.ASSIGNED)
