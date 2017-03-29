from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.http.request import QueryDict
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from mystery_shopping.users.roles import UserRole
from mystery_shopping.factories.companies import CompanyElementFactory
from mystery_shopping.factories.projects import ProjectFactory, EvaluationFactory
from mystery_shopping.factories.questionnaires import QuestionnaireFactory, QuestionnaireTemplateFactory, \
    QuestionnaireBlockFactory, IndicatorQuestionFactory
from mystery_shopping.factories.tenants import TenantFactory
from mystery_shopping.factories.users import UserFactory, TenantProductManagerGroupFactory, DetractorRespondentFactory
from mystery_shopping.users.models import DetractorRespondent
from mystery_shopping.users.tests.user_authentication import AuthenticateUser


class ShopperAPITestCase(APITestCase):
    def setUp(self):
        self.tenant = TenantFactory()
        self.authentication = AuthenticateUser(tenant=self.tenant)
        self.client = self.authentication.client
        self.questionnaire_template = QuestionnaireTemplateFactory(tenant=self.tenant)
        self.project = ProjectFactory(tenant=self.tenant)
        self.company_element = CompanyElementFactory(tenant=self.tenant)

    def test_detractors_with_one_indicator_in_filter(self):
        indicator_1 = 'NPS'
        indicator_2 = 'Plăcere'
        query_params = QueryDict('indicators={}&project={}'.format(indicator_1,
                                                                   self.project.id))
        self._create_detractor_with_indicators([indicator_1, indicator_2])
        self._create_detractor_with_indicators([indicator_1])
        response = self.client.get('{}?{}'.format(reverse('detractorrespondent-list'), query_params.urlencode()))

        self.assertEqual(response.data.get('count'), 2)

    def test_detractors_with_two_indicator_in_filter(self):
        indicator_1 = 'NPS'
        indicator_2 = 'Plăcere'
        query_params = QueryDict('indicators={}&indicators={}&project={}'.format(indicator_1,
                                                                                 indicator_2,
                                                                                 self.project.id))
        self._create_detractor_with_indicators([indicator_1, indicator_2])
        self._create_detractor_with_indicators([indicator_1])
        response = self.client.get('{}?{}'.format(reverse('detractorrespondent-list'), query_params.urlencode()))

        self.assertEqual(response.data.get('count'), 1)

    def _create_detractor_with_indicators(self, indicators):
        questionnaire = QuestionnaireFactory(template=self.questionnaire_template)
        block = QuestionnaireBlockFactory(questionnaire=questionnaire)
        for indicator in indicators:
            IndicatorQuestionFactory(questionnaire=questionnaire, block=block,
                                     additional_info=indicator, score=0)

        evaluation = EvaluationFactory(project=self.project, questionnaire=questionnaire)
        DetractorRespondentFactory(evaluation=evaluation, number_of_questions=len(indicators))
