from django.test.testcases import TestCase
from rest_framework.reverse import reverse

from mystery_shopping.factories.companies import EntityFactory
from mystery_shopping.factories.cxi import WhyCauseFactory, CodedCauseFactory
from mystery_shopping.factories.projects import ResearchMethodologyFactory, ProjectFactory, EvaluationFactory
from mystery_shopping.factories.questionnaires import QuestionnaireTemplateFactory, QuestionTemplateFactory, \
    QuestionnaireFactory, QuestionnaireBlockFactory, IndicatorQuestionFactory
from mystery_shopping.users.tests.user_authentication import AuthenticateUser


class WhyCauseTestCase(TestCase):
    def setUp(self):
        self.authentication = AuthenticateUser()
        self.client = self.authentication.client
        self.tenant = self.authentication.tenant

        # Dependency between QuestionnaireTemplate and ResearchMethodology
        self.questionnaire_template = QuestionnaireTemplateFactory(tenant=self.tenant)
        research_methodology = ResearchMethodologyFactory(tenant=self.tenant)
        research_methodology.questionnaires.add(self.questionnaire_template)

        self.indicator_type = 'random'

        self.entity = EntityFactory(tenant=self.tenant)
        self.template_indicator_question = QuestionTemplateFactory(
            questionnaire_template=self.questionnaire_template,
            type='i',
            additional_info=self.indicator_type)

        # Dependency between Project and ResearchMethodology
        self.project = ProjectFactory(research_methodology=research_methodology,
                                             tenant=self.tenant)

        # Dependency between Project Evaluation and Questionnaire
        self.questionnaire1 = QuestionnaireFactory(template=self.questionnaire_template,
                                                          title='first')
        self.evaluation1 = EvaluationFactory(project=self.project,
                                             questionnaire=self.questionnaire1,
                                             entity=self.entity)

    def _test_if_coded_cause_is_added_to_why_cause_single(self):
        question = self._generate_indicator_question(additional_info=self.indicator_type,
                                                     score=10,
                                                     question_template=self.template_indicator_question)
        why_cause = WhyCauseFactory(question=question)
        coded_cause_to_add = CodedCauseFactory(tenant=self.tenant)
        data = [{
            'id': why_cause.id,
            'coded_causes': [coded_cause_to_add.id]
        }]
        endpoint = reverse('whycause-encode') + '?project={}'.format(str(self.project.id))
        self.client.put(endpoint, data, format='json')
        self.assertEqual(why_cause.coded_causes.first(), coded_cause_to_add)

    def _test_if_coded_cause_is_added_to_why_cause_multiple_why_causes(self):
        question = self._generate_indicator_question(additional_info=self.indicator_type,
                                                     score=10,
                                                     question_template=self.template_indicator_question)
        why_cause_1 = WhyCauseFactory(question=question)
        why_cause_2 = WhyCauseFactory(question=question)
        coded_cause_to_add = CodedCauseFactory(tenant=self.tenant)
        data = [{
            'id': why_cause_1.id,
            'coded_causes': [coded_cause_to_add.id]
        },
        {
            'id': why_cause_2.id,
            'coded_causes': [coded_cause_to_add.id]
        }
        ]
        endpoint = reverse('whycause-encode') + '?project={}'.format(str(self.project.id))
        self.client.put(endpoint, data, format='json')
        self.assertEqual(why_cause_1.coded_causes.first(), coded_cause_to_add)
        self.assertEqual(why_cause_2.coded_causes.first(), coded_cause_to_add)

    def _generate_indicator_question(self, additional_info, score, question_template):
        block1 = QuestionnaireBlockFactory(questionnaire=self.questionnaire1)
        return IndicatorQuestionFactory(questionnaire=self.questionnaire1,
                                        block=block1,
                                        additional_info=additional_info,
                                        score=score,
                                        template_question=question_template, type='i')
