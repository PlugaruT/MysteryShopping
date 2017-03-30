from django.http.request import QueryDict
from rest_framework import status
from rest_framework.reverse import reverse

from rest_framework.test import APITestCase

from mystery_shopping.factories.companies import CompanyElementFactory
from mystery_shopping.factories.projects import ProjectFactory, EvaluationFactory, ResearchMethodologyFactory
from mystery_shopping.factories.questionnaires import QuestionnaireBlockFactory, IndicatorQuestionFactory, \
    QuestionnaireFactory, QuestionnaireTemplateFactory, QuestionTemplateFactory
from mystery_shopping.projects.constants import EvaluationStatus
from mystery_shopping.users.tests.user_authentication import AuthenticateUser


class RespondentsDistributionAPITestCase(APITestCase):
    def setUp(self):
        self.authentication = AuthenticateUser()
        self.client = self.authentication.client
        user = self.authentication.user
        self.questionnaire_template = QuestionnaireTemplateFactory.create(tenant=user.tenant)
        research_methodology = ResearchMethodologyFactory.create(tenant=user.tenant)
        research_methodology.questionnaires.add(self.questionnaire_template)

        self.indicator_type = 'random'

        self.company_element = CompanyElementFactory.create(tenant=user.tenant)
        self.template_indicator_question = QuestionTemplateFactory.create(
            questionnaire_template=self.questionnaire_template, type='i', additional_info=self.indicator_type)

        self.project = ProjectFactory.create(research_methodology=research_methodology)

        self.questionnaire1 = QuestionnaireFactory.create(template=self.questionnaire_template, title='first')
        self.evaluation1 = EvaluationFactory.create(project=self.project, questionnaire=self.questionnaire1,
                                                    company_element=self.company_element,
                                                    status=EvaluationStatus.APPROVED)
        self.questionnaire2 = QuestionnaireFactory.create(template=self.questionnaire_template, title='second')
        self.evaluation2 = EvaluationFactory.create(project=self.project, questionnaire=self.questionnaire2,
                                                    company_element=self.company_element,
                                                    status=EvaluationStatus.APPROVED)

    def test_when_there_are_no_completed_questionnaires_for_other_indicators(self):
        query_params = QueryDict('indicator={}&project={}&company_element={}'.format(self.indicator_type,
                                                                                     self.project.id,
                                                                                     self.company_element.id))
        expected_response = [
            {'value': 0.0, 'key': 'NEGATIVE'},
            {'value': 0.0, 'key': 'POSITIVE'},
            {'value': 0.0, 'key': 'NEUTRAL'}]
        response = self.client.get('{}?{}'.format(reverse('cxi:respondents-distribution'), query_params.urlencode()))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(expected_response, response.data)

    def test_when_there_are_no_completed_questionnaires_for_nps_indicator(self):
        indicator_name = 'NPS'
        query_params = QueryDict('indicator={}&project={}&company_element={}'.format(indicator_name,
                                                                                     self.project.id,
                                                                                     self.company_element.id))
        expected_response = [
            {'value': 0.0, 'key': 'DETRACTOR'},
            {'value': 0.0, 'key': 'PROMOTERS'},
            {'value': 0.0, 'key': 'PASSIVE'}]
        response = self.client.get('{}?{}'.format(reverse('cxi:respondents-distribution'), query_params.urlencode()))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(expected_response, response.data)

    def test_when_there_are_one_negative_and_one_neutral_questionnaires(self):
        query_params = QueryDict('indicator={}&project={}&company_element={}'.format(self.indicator_type,
                                                                                     self.project.id,
                                                                                     self.company_element.id))
        self._generate_first_indicator_question(8, self.indicator_type)
        self._generate_second_indicator_question(2, self.indicator_type)
        expected_response = [
            {'value': 50.0, 'key': 'NEUTRAL'},
            {'value': 50.0, 'key': 'NEGATIVE'},
            {'value': 0.0, 'key': 'POSITIVE'}
        ]
        response = self.client.get('{}?{}'.format(reverse('cxi:respondents-distribution'), query_params.urlencode()))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(expected_response, response.data)

    def test_when_there_are_one_negative_and_one_positive_questionnaires(self):
        query_params = QueryDict('indicator={}&project={}&company_element={}'.format(self.indicator_type,
                                                                                     self.project.id,
                                                                                     self.company_element.id))
        self._generate_first_indicator_question(9, self.indicator_type)
        self._generate_second_indicator_question(2, self.indicator_type)
        expected_response = [
            {'value': 0.0, 'key': 'NEUTRAL'},
            {'value': 50.0, 'key': 'NEGATIVE'},
            {'value': 50.0, 'key': 'POSITIVE'}
        ]
        response = self.client.get('{}?{}'.format(reverse('cxi:respondents-distribution'), query_params.urlencode()))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(expected_response, response.data)

    def test_when_there_are_one_detractor_and_one_promoter_questionnaires_for_nps(self):
        indicator_name = 'NPS'
        query_params = QueryDict('indicator={}&project={}&company_element={}'.format(indicator_name,
                                                                                     self.project.id,
                                                                                     self.company_element.id))
        self._generate_first_indicator_question(9, indicator_name)
        self._generate_second_indicator_question(2, indicator_name)
        expected_response = [
            {'value': 0.0, 'key': 'PASSIVE'},
            {'value': 50.0, 'key': 'DETRACTOR'},
            {'value': 50.0, 'key': 'PROMOTERS'}
        ]
        response = self.client.get('{}?{}'.format(reverse('cxi:respondents-distribution'), query_params.urlencode()))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(expected_response, response.data)

    def _generate_first_indicator_question(self, score, indicator_name):
        block1 = QuestionnaireBlockFactory(questionnaire=self.questionnaire1)
        return IndicatorQuestionFactory.create(questionnaire=self.questionnaire1,
                                               block=block1,
                                               additional_info=indicator_name,
                                               score=score,
                                               template_question=self.template_indicator_question)

    def _generate_second_indicator_question(self, score, indicator_name):
        block2 = QuestionnaireBlockFactory(questionnaire=self.questionnaire2)
        return IndicatorQuestionFactory.create(questionnaire=self.questionnaire2,
                                               block=block2,
                                               additional_info=indicator_name,
                                               score=score,
                                               template_question=self.template_indicator_question)
