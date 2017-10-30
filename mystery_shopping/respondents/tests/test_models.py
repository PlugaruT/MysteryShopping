from django.test import TestCase
from django_fsm_log.models import StateLog
from datetime import date, timedelta

from mystery_shopping.factories.respondents import RespondentCaseFactory
from mystery_shopping.factories.users import UserFactory
from mystery_shopping.respondents.models import RespondentCase


class DetractorCase(TestCase):
    def _assert_comment_equal(self, case, comment_text, comment_user=None):
        self.assertEqual(case.comments.count(), 1)
        comment = case.comments.all()[0]
        self.assertEqual(comment.text, comment_text)
        if comment_user:
            self.assertEqual(comment.author,  comment_user)

    def _assert_state_log_equal(self, case, state):
        logs = StateLog.objects.for_(case).all()
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0].state, state)

    def test_that_case_is_created_assigned(self):
        case = RespondentCaseFactory()

        self.assertEqual(case.state, RespondentCase.STATE.ASSIGNED)

    def test_case_escalation(self):
        case = RespondentCaseFactory()

        case.escalate('reason')

        self.assertEqual(case.state, RespondentCase.STATE.ESCALATED)
        self._assert_comment_equal(case, 'reason')
        self._assert_state_log_equal(case, RespondentCase.STATE.ESCALATED)

    def test_case_assignment(self):
        case = RespondentCaseFactory(state=RespondentCase.STATE.ESCALATED)
        to_user = UserFactory()
        manager = UserFactory()

        case.assign(to=to_user, comment='reason', user=manager)

        self.assertEqual(case.state, RespondentCase.STATE.ASSIGNED)
        self._assert_comment_equal(case, 'reason')
        self._assert_state_log_equal(case, RespondentCase.STATE.ASSIGNED)

    def test_case_start_analysing(self):
        case = RespondentCaseFactory()

        case.start_analysis()

        self.assertEqual(case.state, RespondentCase.STATE.ANALYSIS)
        self._assert_state_log_equal(case, RespondentCase.STATE.ANALYSIS)

    def test_case_analyse(self):
        case = RespondentCaseFactory(state=RespondentCase.STATE.ANALYSIS)

        case.analyse(issue='the issue', issue_tags=('tag1', 'tag2'))

        self.assertEqual(case.state, RespondentCase.STATE.IMPLEMENTATION)
        self.assertEqual(case.issue, 'the issue')
        self.assertEqual(case.issue_tags.count(), 2)
        self._assert_state_log_equal(case, RespondentCase.STATE.IMPLEMENTATION)

    def test_case_implement_no_followup(self):
        case = RespondentCaseFactory(state=RespondentCase.STATE.IMPLEMENTATION)

        case.implement(solution='the solution', solution_tags=('tag1', 'tag2'))

        self.assertEqual(case.state, RespondentCase.STATE.SOLVED)
        self.assertEqual(case.solution, 'the solution')
        self.assertEqual(case.solution_tags.count(), 2)
        self._assert_state_log_equal(case, RespondentCase.STATE.SOLVED)

    def test_case_implement_with_followup(self):
        case = RespondentCaseFactory(state=RespondentCase.STATE.IMPLEMENTATION)
        follow_up_date = date.today() + timedelta(days=5)
        follow_up_user = UserFactory()

        case.implement(solution='the solution', solution_tags=('tag1', 'tag2'),
                       follow_up_date=follow_up_date, follow_up_user=follow_up_user)

        self.assertEqual(case.state, RespondentCase.STATE.FOLLOW_UP)
        self.assertEqual(case.solution, 'the solution')
        self.assertEqual(case.solution_tags.count(), 2)
        self.assertEqual(case.follow_up_date, follow_up_date)
        self.assertEqual(case.follow_up_user, follow_up_user)
        self._assert_state_log_equal(case, RespondentCase.STATE.FOLLOW_UP)

    def test_case_follow_up(self):
        case = RespondentCaseFactory(state=RespondentCase.STATE.FOLLOW_UP)

        case.follow_up(follow_up='the follow up', follow_up_tags=('tag1', 'tag2'))

        self.assertEqual(case.state, RespondentCase.STATE.SOLVED)
        self.assertEqual(case.follow_up, 'the follow up')
        self.assertEqual(case.follow_up_tags.count(), 2)
        self._assert_state_log_equal(case, RespondentCase.STATE.SOLVED)

    def test_case_close_no_user(self):
        case = RespondentCaseFactory()

        case.close(reason='because')

        self.assertEqual(case.state, RespondentCase.STATE.CLOSED)
        self._assert_comment_equal(case, 'because', case.responsible_user)
        self._assert_state_log_equal(case, RespondentCase.STATE.CLOSED)

    def test_case_close_with_user(self):
        case = RespondentCaseFactory(state=RespondentCase.STATE.IMPLEMENTATION)
        user = UserFactory()

        case.close(reason='because', user=user)

        self.assertEqual(case.state, RespondentCase.STATE.CLOSED)
        self._assert_comment_equal(case, 'because', user)
        self._assert_state_log_equal(case, RespondentCase.STATE.CLOSED)
