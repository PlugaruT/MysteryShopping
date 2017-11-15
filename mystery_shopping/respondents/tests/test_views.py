from datetime import timedelta
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.http import QueryDict
from django_fsm_log.models import StateLog
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from mystery_shopping.factories.common import TagFactory
from mystery_shopping.factories.projects import EvaluationFactory, ProjectFactory
from mystery_shopping.factories.respondents import RespondentCaseFactory, RespondentFactory
from mystery_shopping.factories.users import UserFactory
from mystery_shopping.users.tests.user_authentication import AuthenticateUser


class RespondentCasesPerStateAPITestCase(APITestCase):
    def setUp(self):
        self.authentication = AuthenticateUser()
        self.client = self.authentication.client
        self.project = ProjectFactory()

    def test_view_with_no_data(self):
        expected_result = [
            {'key': 'ASSIGNED', 'value': 0, 'additional': 0},
            {'key': 'ESCALATED', 'value': 0, 'additional': 0},
            {'key': 'ANAL', 'value': 0, 'additional': 0},
            {'key': 'IMPLEMENTATION', 'value': 0, 'additional': 0},
            {'key': 'FOLLOW_UP', 'value': 0, 'additional': 0},
            {'key': 'SOLVED', 'value': 0, 'additional': 0},
            {'key': 'CLOSED', 'value': 0, 'additional': 0},
        ]
        query_params = QueryDict('project={}'.format(self.project.id))

        response = self.client.get('{}?{}'.format(reverse('respondents:cases-per-state'), query_params.urlencode()))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertCountEqual(expected_result, response.data)

    def test_view_with_data(self):
        self._create_cases()
        expected_result = [
            {'key': 'ASSIGNED', 'value': 1, 'additional': 0},
            {'key': 'ESCALATED', 'value': 0, 'additional': 0},
            {'key': 'ANAL', 'value': 2, 'additional': 0},
            {'key': 'IMPLEMENTATION', 'value': 0, 'additional': 0},
            {'key': 'FOLLOW_UP', 'value': 0, 'additional': 0},
            {'key': 'SOLVED', 'value': 0, 'additional': 0},
            {'key': 'CLOSED', 'value': 1, 'additional': 0},
        ]

        query_params = QueryDict('project={}'.format(self.project.id))

        response = self.client.get('{}?{}'.format(reverse('respondents:cases-per-state'), query_params.urlencode()))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertCountEqual(expected_result, response.data)

    def _create_cases(self):
        evaluation = EvaluationFactory(project=self.project)
        respondent_1 = RespondentFactory(evaluation=evaluation)
        respondent_2 = RespondentFactory(evaluation=evaluation)
        respondent_3 = RespondentFactory(evaluation=evaluation)
        respondent_4 = RespondentFactory(evaluation=evaluation)
        RespondentCaseFactory(state='ANAL', respondent=respondent_1)
        RespondentCaseFactory(state='ASSIGNED', respondent=respondent_2)
        RespondentCaseFactory(state='CLOSED', respondent=respondent_3)
        RespondentCaseFactory(state='ANAL', respondent=respondent_4)


class AverageProcessingTimePerStateAPITestCase(APITestCase):
    def setUp(self):
        self.authentication = AuthenticateUser()
        self.client = self.authentication.client

        self.project = ProjectFactory()

    def test_view_with_no_data(self):
        expected_result = [
            {'key': 'ASSIGNED', 'value': 0, 'additional': 0},
            {'key': 'ESCALATED', 'value': 0, 'additional': 0},
            {'key': 'ANAL', 'value': 0, 'additional': 0},
            {'key': 'IMPLEMENTATION', 'value': 0, 'additional': 0},
            {'key': 'FOLLOW_UP', 'value': 0, 'additional': 0},
        ]

        query_params = QueryDict('project={}'.format(self.project.id))
        response = self.client.get('{}?{}'.format(reverse('respondents:time-per-state'), query_params.urlencode()))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertListEqual(expected_result, response.data)

    def test_view_with_data(self):
        states = ['ASSIGNED', 'ESCALATED', 'ASSIGNED', 'ANAL', 'IMPLEMENTATION', 'FOLLOW_UP', 'SOLVED']
        self._generate_cases(states)
        expected_result = [
            {'key': 'ASSIGNED', 'value': 5400, 'additional': 0},
            {'key': 'ESCALATED', 'value': 5400, 'additional': 0},
            {'key': 'ANAL', 'value': 5400, 'additional': 0},
            {'key': 'IMPLEMENTATION', 'value': 5400, 'additional': 0},
            {'key': 'FOLLOW_UP', 'value': 5400, 'additional': 0},
        ]

        query_params = QueryDict('project={}'.format(self.project.id))
        response = self.client.get('{}?{}'.format(reverse('respondents:time-per-state'), query_params.urlencode()))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertListEqual(expected_result, response.data)

    def test_view_with_incomplete_data(self):
        states = ['ASSIGNED', 'ANAL', 'IMPLEMENTATION', 'SOLVED']
        self._generate_cases(states)
        expected_result = [
            {'key': 'ASSIGNED', 'value': 5400, 'additional': 0},
            {'key': 'ESCALATED', 'value': 0, 'additional': 0},
            {'key': 'ANAL', 'value': 5400, 'additional': 0},
            {'key': 'IMPLEMENTATION', 'value': 5400, 'additional': 0},
            {'key': 'FOLLOW_UP', 'value': 0, 'additional': 0},
        ]

        query_params = QueryDict('project={}'.format(self.project.id))
        response = self.client.get('{}?{}'.format(reverse('respondents:time-per-state'), query_params.urlencode()))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertListEqual(expected_result, response.data)

    def test_view_with_active_cases(self):
        states = ['ASSIGNED', 'ANAL', 'IMPLEMENTATION']
        self._generate_cases(states)
        expected_result = [
            {'key': 'ASSIGNED', 'value': 5400, 'additional': 0},
            {'key': 'ESCALATED', 'value': 0, 'additional': 0},
            {'key': 'ANAL', 'value': 5400, 'additional': 0},
            {'key': 'IMPLEMENTATION', 'value': 5400, 'additional': 0},
            {'key': 'FOLLOW_UP', 'value': 0, 'additional': 0},
        ]

        query_params = QueryDict('project={}'.format(self.project.id))
        response = self.client.get('{}?{}'.format(reverse('respondents:time-per-state'), query_params.urlencode()))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertListEqual(expected_result, response.data)

    def _generate_cases(self, states):
        evaluation = EvaluationFactory(project=self.project)
        respondent_1 = RespondentFactory(evaluation=evaluation)
        respondent_2 = RespondentFactory(evaluation=evaluation)
        case1 = RespondentCaseFactory(respondent=respondent_1)
        case2 = RespondentCaseFactory(respondent=respondent_2)

        self._generate_logs(case1, states, delta_hours=1)
        self._generate_logs(case2, states, delta_hours=2)

    @staticmethod
    def _generate_logs(respondent_case, states, delta_hours):
        ct = ContentType.objects.get_for_model(respondent_case)
        time = timezone.now() - timedelta(hours=delta_hours * len(states))

        for state in states:
            StateLog.objects.create(content_type=ct, object_id=respondent_case.id,
                                    transition='tr', state=state, timestamp=time)
            time += timedelta(hours=delta_hours)


class RespondentCasesPerSolutionTagAPITestCase(APITestCase):
    def setUp(self):
        self.authentication = AuthenticateUser()
        self.client = self.authentication.client
        self.project = ProjectFactory()

        self.tag_1 = TagFactory(name='tag_1')
        self.tag_2 = TagFactory(name='tag_2')
        self.tag_3 = TagFactory(name='tag_3')

    def test_view_with_no_data(self):
        expected_data = []

        query_params = QueryDict('project={}'.format(self.project.id))

        response = self.client.get('{}?{}'.format(reverse('respondents:cases-per-solution-tag'),
                                                  query_params.urlencode()))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertCountEqual(expected_data, response.data)

    def test_view_with_data(self):
        self._generate_cases_with_tags()
        expected_data = [
            {'key': self.tag_1.name, 'value': 2, 'additional': 0},
            {'key': self.tag_2.name, 'value': 3, 'additional': 0},
            {'key': self.tag_3.name, 'value': 2, 'additional': 0}
        ]

        query_params = QueryDict('project={}'.format(self.project.id))

        response = self.client.get('{}?{}'.format(reverse('respondents:cases-per-solution-tag'),
                                                  query_params.urlencode()))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertCountEqual(expected_data, response.data)

    def _generate_cases_with_tags(self):
        evaluation = EvaluationFactory(project=self.project)
        respondent_1 = RespondentFactory(evaluation=evaluation)
        respondent_2 = RespondentFactory(evaluation=evaluation)
        respondent_3 = RespondentFactory(evaluation=evaluation)
        respondent_4 = RespondentFactory(evaluation=evaluation)
        RespondentCaseFactory(solution_tags=(self.tag_1, self.tag_2), respondent=respondent_1)
        RespondentCaseFactory(solution_tags=(self.tag_2,), respondent=respondent_2)
        RespondentCaseFactory(solution_tags=(self.tag_3,), respondent=respondent_3)
        RespondentCaseFactory(solution_tags=(self.tag_1, self.tag_2, self.tag_3), respondent=respondent_4)


class RespondentCasesPerIssueTagAPITestCase(APITestCase):
    def setUp(self):
        self.authentication = AuthenticateUser()
        self.client = self.authentication.client
        self.project = ProjectFactory()

        self.tag_1 = TagFactory(name='tag_1')
        self.tag_2 = TagFactory(name='tag_2')
        self.tag_3 = TagFactory(name='tag_3')

    def test_view_with_no_data(self):
        expected_data = []

        query_params = QueryDict('project={}'.format(self.project.id))

        response = self.client.get('{}?{}'.format(reverse('respondents:cases-per-issue-tag'),
                                                  query_params.urlencode()))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertCountEqual(expected_data, response.data)

    def test_view_with_data(self):
        self._generate_cases_with_tags()
        expected_data = [
            {'key': self.tag_1.name, 'value': 2, 'additional': 0},
            {'key': self.tag_2.name, 'value': 4, 'additional': 0},
            {'key': self.tag_3.name, 'value': 2, 'additional': 0}
        ]
        response = self.client.get(reverse('respondents:cases-per-issue-tag'))

        query_params = QueryDict('project={}'.format(self.project.id))

        response = self.client.get('{}?{}'.format(reverse('respondents:cases-per-issue-tag'),
                                                  query_params.urlencode()))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertCountEqual(expected_data, response.data)

    def _generate_cases_with_tags(self):
        evaluation = EvaluationFactory(project=self.project)
        respondent_1 = RespondentFactory(evaluation=evaluation)
        respondent_2 = RespondentFactory(evaluation=evaluation)
        respondent_3 = RespondentFactory(evaluation=evaluation)
        respondent_4 = RespondentFactory(evaluation=evaluation)
        RespondentCaseFactory(issue_tags=(self.tag_1, self.tag_2), respondent=respondent_1)
        RespondentCaseFactory(issue_tags=(self.tag_2,), respondent=respondent_2)
        RespondentCaseFactory(issue_tags=(self.tag_3, self.tag_2), respondent=respondent_3)
        RespondentCaseFactory(issue_tags=(self.tag_1, self.tag_2, self.tag_3), respondent=respondent_4)


class RespondentCasesPerUserAPITestCase(APITestCase):
    def setUp(self):
        self.authentication = AuthenticateUser()
        self.client = self.authentication.client
        self.project = ProjectFactory()
        self.user_1 = UserFactory()
        self.user_2 = UserFactory()
        self.user_3 = UserFactory()

    def test_view_with_no_data(self):
        expected_data = []

        query_params = QueryDict('project={}'.format(self.project.id))
        response = self.client.get('{}?{}'.format(reverse('respondents:cases-per-user'), query_params.urlencode()))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertCountEqual(expected_data, response.data)

    def test_view_with_data(self):
        self._generate_cases_with_responsible_users()
        expected_data = [
            {'key': '{} {}'.format(self.user_1.first_name, self.user_1.last_name), 'value': 2, 'additional': 0},
            {'key': '{} {}'.format(self.user_2.first_name, self.user_2.last_name), 'value': 1, 'additional': 0},
            {'key': '{} {}'.format(self.user_3.first_name, self.user_3.last_name), 'value': 1, 'additional': 0}
        ]

        query_params = QueryDict('project={}'.format(self.project.id))
        response = self.client.get('{}?{}'.format(reverse('respondents:cases-per-user'), query_params.urlencode()))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertCountEqual(expected_data, response.data)

    def _generate_cases_with_responsible_users(self):
        evaluation = EvaluationFactory(project=self.project)
        respondent_1 = RespondentFactory(evaluation=evaluation)
        respondent_2 = RespondentFactory(evaluation=evaluation)
        respondent_3 = RespondentFactory(evaluation=evaluation)
        respondent_4 = RespondentFactory(evaluation=evaluation)
        RespondentCaseFactory(responsible_user=self.user_1, respondent=respondent_1)
        RespondentCaseFactory(responsible_user=self.user_1, respondent=respondent_2)
        RespondentCaseFactory(responsible_user=self.user_3, respondent=respondent_3)
        RespondentCaseFactory(responsible_user=self.user_2, respondent=respondent_4)
