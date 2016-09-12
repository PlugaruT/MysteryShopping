from django.test.testcases import TestCase
from json import loads, dumps

from mystery_shopping.factories.companies import EntityFactory
from mystery_shopping.factories.projects import ProjectFactory
from mystery_shopping.factories.questionnaires import QuestionnaireTemplateFactory, QuestionTemplateFactory, \
    QuestionnaireTemplateBlockFactory
from mystery_shopping.factories.tenants import TenantFactory
from mystery_shopping.factories.users import ShopperFactory, UserFactory
from mystery_shopping.projects.serializers import EvaluationSerializer
from mystery_shopping.questionnaires.models import CrossIndexTemplate, CrossIndexQuestionTemplate


class TestSerializeCrossIndexForQuestionnaire(TestCase):
    def setUp(self):
        self.tenant = TenantFactory()
        project = ProjectFactory()
        shopper = ShopperFactory()
        saved_by_user = UserFactory()
        entity = EntityFactory()
        self.template_questionnaire = QuestionnaireTemplateFactory(tenant=self.tenant)

        self.template_block = QuestionnaireTemplateBlockFactory(questionnaire_template=self.template_questionnaire)

        self.template_question_1 = QuestionTemplateFactory(
            questionnaire_template=self.template_questionnaire, question_body='first template question',
            template_block=self.template_block)
        self.template_question_2 = QuestionTemplateFactory(
            questionnaire_template=self.template_questionnaire, question_body='second template question',
            template_block=self.template_block)

        self.template_cross_index_1 = CrossIndexTemplate.objects.create(
            questionnaire_template=self.template_questionnaire)
        self.template_cross_index_2 = CrossIndexTemplate.objects.create(
            questionnaire_template=self.template_questionnaire)

        cross_index_question_template_0 = CrossIndexQuestionTemplate.objects.create(
            template_cross_index=self.template_cross_index_1, template_question=self.template_question_2, weight=11)

        cross_index_question_template_1 = CrossIndexQuestionTemplate.objects.create(
            template_cross_index=self.template_cross_index_1, template_question=self.template_question_1, weight=10)

        cross_index_question_template_2 = CrossIndexQuestionTemplate.objects.create(
            template_cross_index=self.template_cross_index_2, template_question=self.template_question_2, weight=20)

        data = {
            'project': project.id,
            'shopper': shopper.id,
            'saved_by_user': saved_by_user.id,
            'questionnaire_template': self.template_questionnaire.id,
            'entity': entity.id,

        }

        self.evaluation = EvaluationSerializer(data=data)
        self.evaluation.is_valid(raise_exception=True)
        self.evaluation.save()

    def _get_cross_index_question(self, template_cross_index, template_question):
        return self.evaluation.instance.questionnaire.cross_indexes.get(
                                template_cross_index=template_cross_index).cross_index_questions.get(
                                question=self._get_question(template_question))

    def _get_cross_index(self, template_cross_index):
        return self.evaluation.instance.questionnaire.cross_indexes.get(
                                template_cross_index=template_cross_index)

    def _get_question(self, template_question):
        return self.evaluation.instance.questionnaire.questions.get(template_question=template_question)

    def test_is_cross_indexes_are_created_accordingly(self):

        expected_result =[
                {
                    'template_cross_index': self.template_cross_index_1.id,
                    'score': None,
                    'questions': [
                        {
                            'id': self._get_cross_index_question(self.template_cross_index_1,
                                                                 self.template_question_2).id,
                            'cross_index': self._get_cross_index(self.template_cross_index_1).id,
                            'question': self._get_question(self.template_question_2).id,
                            'weight': '11.00'
                        },
                        {
                            'id': self._get_cross_index_question(self.template_cross_index_1,
                                                                 self.template_question_1).id,
                            'cross_index': self._get_cross_index(self.template_cross_index_1).id,
                            'question': self._get_question(self.template_question_1).id,
                            'weight': '10.00'
                        }
                    ],
                    'id': self._get_cross_index(self.template_cross_index_1).id,
                    'questionnaire': self.evaluation.instance.questionnaire.id,
                    'title': ''
                },
                {
                    'template_cross_index': self.template_cross_index_2.id,
                    'score': None,
                    'questions': [
                        {
                            'id': self._get_cross_index_question(self.template_cross_index_2,
                                                                 self.template_question_2).id,
                            'cross_index': self._get_cross_index(self.template_cross_index_2).id,
                            'question': self._get_question(self.template_question_2).id,
                            'weight': '20.00'
                        }
                    ],
                    'id': self._get_cross_index(self.template_cross_index_2).id,
                    'questionnaire': self.evaluation.instance.questionnaire.id,
                    'title': ''
                }
            ]

        result = loads(dumps(self.evaluation.data['questionnaire']['cross_indexes']))
        self.assertEquals(expected_result, result)
