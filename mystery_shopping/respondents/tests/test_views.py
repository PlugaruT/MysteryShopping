from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from mystery_shopping.factories.common import TagFactory
from mystery_shopping.factories.respondents import RespondentCaseFactory
from mystery_shopping.users.tests.user_authentication import AuthenticateUser


class RespondentCasesPerStateAPITestCase(APITestCase):
    def setUp(self):
        self.authentication = AuthenticateUser()
        self.client = self.authentication.client

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

        response = self.client.get(reverse('respondents:cases-per-state'))

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

        response = self.client.get(reverse('respondents:cases-per-state'))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertCountEqual(expected_result, response.data)

    @staticmethod
    def _create_cases():
        RespondentCaseFactory(state='ANAL')
        RespondentCaseFactory(state='ASSIGNED')
        RespondentCaseFactory(state='CLOSED')
        RespondentCaseFactory(state='ANAL')


class RespondentCasesPerSolutionTagAPITestCase(APITestCase):
    def setUp(self):
        self.authentication = AuthenticateUser()
        self.client = self.authentication.client

        tag_type = 'RESPONDENT_CASE_SOLUTION'

        self.tag_1 = TagFactory(type=tag_type)
        self.tag_2 = TagFactory(type=tag_type)
        self.tag_3 = TagFactory(type=tag_type)

    def test_view_with_no_data(self):
        expected_data = []
        response = self.client.get(reverse('respondents:cases-per-solution-tag'))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertCountEqual(expected_data, response.data)

    def test_view_with_data(self):
        expected_data = [
            {'key': self.tag_1.name, 'value': 2, 'additional': 0},
            {'key': self.tag_2.name, 'value': 3, 'additional': 0},
            {'key': self.tag_3.name, 'value': 2, 'additional': 0}
        ]
        response = self.client.get(reverse('respondents:cases-per-solution-tag'))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertCountEqual(expected_data, response.data)

    def _generate_cases_with_tags(self):
        RespondentCaseFactory(tags=(self.tag_1, self.tag_2))
        RespondentCaseFactory(tags=(self.tag_2,))
        RespondentCaseFactory(tags=(self.tag_3,))
        RespondentCaseFactory(tags=(self.tag_1, self.tag_2, self.tag_3))


class RespondentCasesPerIssueTagAPITestCase(APITestCase):
    def setUp(self):
        self.authentication = AuthenticateUser()
        self.client = self.authentication.client
        tag_type = 'RESPONDENT_CASE_ISSUE'

        self.tag_1 = TagFactory(type=tag_type)
        self.tag_2 = TagFactory(type=tag_type)
        self.tag_3 = TagFactory(type=tag_type)

    def test_view_with_no_data(self):
        expected_data = []
        response = self.client.get(reverse('respondents:cases-per-issue-tag'))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertCountEqual(expected_data, response.data)

    def test_view_with_data(self):
        expected_data = [
            {'key': self.tag_1.name, 'value': 2, 'additional': 0},
            {'key': self.tag_2.name, 'value': 4, 'additional': 0},
            {'key': self.tag_3.name, 'value': 2, 'additional': 0}
        ]
        response = self.client.get(reverse('respondents:cases-per-issue-tag'))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertCountEqual(expected_data, response.data)

    def _generate_cases_with_tags(self):
        RespondentCaseFactory(tags=(self.tag_1, self.tag_2))
        RespondentCaseFactory(tags=(self.tag_2,))
        RespondentCaseFactory(tags=(self.tag_3, self.tag_2))
        RespondentCaseFactory(tags=(self.tag_1, self.tag_2, self.tag_3))
