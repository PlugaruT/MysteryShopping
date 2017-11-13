from django.http import QueryDict
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from mystery_shopping.factories.respondents import RespondentCaseFactory
from mystery_shopping.respondents.models import RespondentCase, Respondent, RespondentCaseState
from mystery_shopping.users.tests.user_authentication import AuthenticateUser

from urllib.parse import urlencode


class RespondentsAPITestCase(APITestCase):
    def setUp(self):
        self.authentication = AuthenticateUser()
        self.client = self.authentication.client

        RespondentCase.objects.all().delete()
        Respondent.objects.all().delete()

    def test_get_respondents_with_cases(self):
        case = RespondentCaseFactory()
        params = {
            'project': case.respondent.evaluation.project_id
        }
        response = self.client.get('{}?{}'.format(reverse('respondentswithcases-list'), urlencode(params)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 1)
        self.assertEqual(response.data.get('results')[0].get('id'), case.respondent.id)


class RespondentCasesAPITestCase(APITestCase):
    def setUp(self):
        self.authentication = AuthenticateUser()
        self.client = self.authentication.client

        RespondentCase.objects.all().delete()

    def test_start_analysis(self):
        case = RespondentCaseFactory()
        case.assign(self.authentication.user)
        case.save()

        response = self.client.post(path=reverse('respondentcases-start-analysis', args=(case.id,)))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        read_case = RespondentCase.objects.get(id=case.id)
        self.assertEqual(read_case.state, RespondentCaseState.ANALYSIS)

    def test_escalate(self):
        case = RespondentCaseFactory()
        case.assign(self.authentication.user)
        case.save()

        response = self.client.post(path=reverse('respondentcases-escalate', args=(case.id,)),
                                    data={'reason': 'because'})

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        read_case = RespondentCase.objects.get(id=case.id)
        self.assertEqual(read_case.state, RespondentCaseState.ESCALATED)
        self.assertEqual(read_case.comments.first().text, 'because')
