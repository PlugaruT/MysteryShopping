from django.test import TestCase
from django_fsm_log.models import StateLog
from datetime import date, timedelta

from mystery_shopping.factories.respondents import RespondentCaseFactory
from mystery_shopping.factories.users import UserFactory
from mystery_shopping.respondents.models import RespondentCase, RespondentCaseState


class DetractorCaseTestCase(TestCase):
    def _assert_comment_equal(self, case, comment_text, comment_user):
        self.assertEqual(case.comments.count(), 1)
        comment = case.comments.all()[0]
        self.assertEqual(comment.text, comment_text)
        self.assertEqual(comment.author,  comment_user)

    def _assert_state_log_equal(self, case, state):
        logs = StateLog.objects.for_(case).all()
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0].state, state)

    def test_that_case_is_created_init(self):
        case = RespondentCaseFactory()

        self.assertEqual(case.state, RespondentCaseState.INIT)

    def test_case_escalation(self):
        case = RespondentCaseFactory(state=RespondentCaseState.ASSIGNED)

        case.escalate('reason')

        self.assertEqual(case.state, RespondentCaseState.ESCALATED)
        self._assert_comment_equal(case, 'reason', case.responsible_user)
        self._assert_state_log_equal(case, RespondentCaseState.ESCALATED)

    def test_case_assignment(self):
        case = RespondentCaseFactory()
        to_user = UserFactory()

        case.assign(to=to_user)

        self.assertEqual(case.state, RespondentCaseState.ASSIGNED)
        self._assert_state_log_equal(case, RespondentCaseState.ASSIGNED)

    def test_case_assignment_from_escalation(self):
        case = RespondentCaseFactory(state=RespondentCaseState.ESCALATED)
        to_user = UserFactory()
        manager = UserFactory()

        case.assign(to=to_user, comment='reason', user=manager)

        self.assertEqual(case.state, RespondentCaseState.ASSIGNED)
        self._assert_comment_equal(case, 'reason', manager)
        self._assert_state_log_equal(case, RespondentCaseState.ASSIGNED)

    def test_case_start_analysing(self):
        case = RespondentCaseFactory(state=RespondentCaseState.ASSIGNED)

        case.start_analysis()

        self.assertEqual(case.state, RespondentCaseState.ANALYSIS)
        self._assert_state_log_equal(case, RespondentCaseState.ANALYSIS)

    def test_case_analyse(self):
        case = RespondentCaseFactory(state=RespondentCaseState.ANALYSIS)

        case.analyse(issue='the issue', issue_tags=('tag1', 'tag2'))

        self.assertEqual(case.state, RespondentCaseState.IMPLEMENTATION)
        self.assertEqual(case.issue, 'the issue')
        self.assertEqual(case.issue_tags.count(), 2)
        self._assert_state_log_equal(case, RespondentCaseState.IMPLEMENTATION)

    def test_case_analyse_no_tags(self):
        case = RespondentCaseFactory(state=RespondentCaseState.ANALYSIS)

        case.analyse(issue='the issue')

        self.assertEqual(case.state, RespondentCaseState.IMPLEMENTATION)
        self.assertEqual(case.issue, 'the issue')
        self.assertEqual(case.issue_tags.count(), 0)
        self._assert_state_log_equal(case, RespondentCaseState.IMPLEMENTATION)

    def test_case_implement_no_followup(self):
        case = RespondentCaseFactory(state=RespondentCaseState.IMPLEMENTATION)

        case.implement(solution='the solution', solution_tags=('tag1', 'tag2'))

        self.assertEqual(case.state, RespondentCaseState.SOLVED)
        self.assertEqual(case.solution, 'the solution')
        self.assertEqual(case.solution_tags.count(), 2)
        self._assert_state_log_equal(case, RespondentCaseState.SOLVED)

    def test_case_implement_no_followup_no_tags(self):
        case = RespondentCaseFactory(state=RespondentCaseState.IMPLEMENTATION)

        case.implement(solution='the solution')

        self.assertEqual(case.state, RespondentCaseState.SOLVED)
        self.assertEqual(case.solution, 'the solution')
        self.assertEqual(case.solution_tags.count(), 0)
        self._assert_state_log_equal(case, RespondentCaseState.SOLVED)

    def test_case_implement_with_followup(self):
        case = RespondentCaseFactory(state=RespondentCaseState.IMPLEMENTATION)
        follow_up_date = date.today() + timedelta(days=5)
        follow_up_user = UserFactory()

        case.implement(solution='the solution', solution_tags=('tag1', 'tag2'),
                       follow_up_date=follow_up_date, follow_up_user=follow_up_user)

        self.assertEqual(case.state, RespondentCaseState.FOLLOW_UP)
        self.assertEqual(case.solution, 'the solution')
        self.assertEqual(case.solution_tags.count(), 2)
        self.assertEqual(case.follow_up_date, follow_up_date)
        self.assertEqual(case.follow_up_user, follow_up_user)
        self._assert_state_log_equal(case, RespondentCaseState.FOLLOW_UP)

    def test_case_follow_up(self):
        case = RespondentCaseFactory(state=RespondentCaseState.FOLLOW_UP)

        case.do_follow_up(follow_up='the follow up', follow_up_tags=('tag1', 'tag2'))

        self.assertEqual(case.state, RespondentCaseState.SOLVED)
        self.assertEqual(case.follow_up, 'the follow up')
        self.assertEqual(case.follow_up_tags.count(), 2)
        self._assert_state_log_equal(case, RespondentCaseState.SOLVED)

    def test_case_follow_up_no_tags(self):
        case = RespondentCaseFactory(state=RespondentCaseState.FOLLOW_UP)

        case.do_follow_up(follow_up='the follow up')

        self.assertEqual(case.state, RespondentCaseState.SOLVED)
        self.assertEqual(case.follow_up, 'the follow up')
        self.assertEqual(case.follow_up_tags.count(), 0)
        self._assert_state_log_equal(case, RespondentCaseState.SOLVED)

    def test_case_close_no_user(self):
        case = RespondentCaseFactory(state=RespondentCaseState.ASSIGNED)

        case.close(reason='because')

        self.assertEqual(case.state, RespondentCaseState.CLOSED)
        self._assert_comment_equal(case, 'because', case.responsible_user)
        self._assert_state_log_equal(case, RespondentCaseState.CLOSED)

    def test_case_close_with_user(self):
        case = RespondentCaseFactory(state=RespondentCaseState.IMPLEMENTATION)
        user = UserFactory()

        case.close(reason='because', user=user)

        self.assertEqual(case.state, RespondentCaseState.CLOSED)
        self._assert_comment_equal(case, 'because', user)
        self._assert_state_log_equal(case, RespondentCaseState.CLOSED)
