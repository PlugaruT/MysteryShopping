from django.http import QueryDict
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from mystery_shopping.factories.respondents import RespondentCaseFactory
from mystery_shopping.respondents.models import RespondentCase
from mystery_shopping.users.tests.user_authentication import AuthenticateUser

from urllib.parse import urlencode


class RespondentsDistributionAPITestCase(APITestCase):
    def setUp(self):
        self.authentication = AuthenticateUser()
        self.client = self.authentication.client

        RespondentCase.objects.all().delete()

    def test_get_cases(self):
        case = RespondentCaseFactory()
        params = {
            'project': case.respondent.evaluation.project_id
        }
        response = self.client.get('{}?{}'.format(reverse('respondentswithcases-list'), urlencode(params)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 1)
        self.assertEqual(response.data.get('results')[0].get('id'), case.respondent.id)
