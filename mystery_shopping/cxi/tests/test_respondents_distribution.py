from django.http.request import QueryDict
from rest_framework import status
from rest_framework.reverse import reverse

from rest_framework.test import APITestCase

from mystery_shopping.factories.companies import CompanyElementFactory
from mystery_shopping.factories.projects import ProjectFactory, EvaluationFactory, ResearchMethodologyFactory
from mystery_shopping.factories.questionnaires import QuestionnaireBlockFactory, IndicatorQuestionFactory, \
    QuestionnaireFactory, QuestionnaireTemplateFactory, QuestionTemplateFactory
from mystery_shopping.questionnaires.models import QuestionnaireQuestion
from mystery_shopping.users.tests.user_authentication import AuthenticateUser


class RespondentsDistributionAPITestCase(APITestCase):
    def setUp(self):
        self.authentification = AuthenticateUser()
        self.client = self.authentification.client
        self.questionnaire_template = QuestionnaireTemplateFactory.create()
        research_methodology = ResearchMethodologyFactory.create()
        research_methodology.questionnaires.add(self.questionnaire_template)

        self.indicator_type = 'NPS'

        self.company_element = CompanyElementFactory.create()
        self.template_indicator_question = QuestionTemplateFactory.create(
            questionnaire_template=self.questionnaire_template, type='i', additional_info=self.indicator_type)

        # Dependency between Project and ResearchMethodology
        self.project = ProjectFactory.create(research_methodology=research_methodology)

        # Dependency between Project Evaluation and Questionnaire
        self.questionnaire1 = QuestionnaireFactory.create(template=self.questionnaire_template, title='first')
        self.evaluation1 = EvaluationFactory.create(project=self.project, questionnaire=self.questionnaire1,
                                                    company_element=self.company_element)
        self.questionnaire2 = QuestionnaireFactory.create(template=self.questionnaire_template, title='second')
        self.evaluation2 = EvaluationFactory.create(project=self.project, questionnaire=self.questionnaire2,
                                                    company_element=self.company_element)
        self.query_params = QueryDict('indicator={}&project={}&company_element={}'.format(self.indicator_type,
                                                                                          self.project.id,
                                                                                          self.company_element.id))

    def test_when_there_are_no_completed_questionnaires(self):
        self._generate_first_indicator_question(5)
        self._generate_second_indicator_question(9)
        print(QuestionnaireQuestion.objects.get_indicator_questions_for_company_elements(
            project=self.project.id, indicator=self.indicator_type).count())
        print(self.query_params)
        expected_response = [
            {'value': 0, 'key': 'CHART.NEGATIVE', 'color': '#f44336'},
            {'value': 0, 'key': 'CHART.POSITIVE', 'color': '#4CAF50'},
            {'value': 0, 'key': 'CHART.NEUTRAL', 'color': '#9E9E9E'}]
        response = self.client.get('{}?{}'.format(reverse('cxi:respondents-distribution'), self.query_params))
        print(response.data)
        self.assertFalse(True)
        self.assertListEqual(expected_response, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def _generate_first_indicator_question(self, score):
        block1 = QuestionnaireBlockFactory(questionnaire=self.questionnaire1)
        return IndicatorQuestionFactory.create(questionnaire=self.questionnaire1,
                                               block=block1,
                                               additional_info=self.indicator_type,
                                               score=score,
                                               template_question=self.template_indicator_question, type='i')

    def _generate_second_indicator_question(self, score):
        block2 = QuestionnaireBlockFactory(questionnaire=self.questionnaire2)
        return IndicatorQuestionFactory.create(questionnaire=self.questionnaire2,
                                               block=block2,
                                               additional_info=self.indicator_type,
                                               score=score,
                                               template_question=self.template_indicator_question, type='i')
