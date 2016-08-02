from django.test.testcases import TestCase
from factory import fuzzy

from mystery_shopping.cxi.algorithms import CollectDataForIndicatorDashboard
from mystery_shopping.factories.companies import EntityFactory
from mystery_shopping.factories.projects import ResearchMethodologyFactory, ProjectFactory, EvaluationFactory
from mystery_shopping.factories.questionnaires import QuestionnaireTemplateFactory, QuestionnaireFactory, \
    IndicatorQuestionFactory, QuestionnaireBlockFactory, QuestionTemplateFactory
from mystery_shopping.projects.models import Project
from mystery_shopping.questionnaires.models import Questionnaire


class TestClassConstructor(TestCase):
    def test_that_project_is_set(self):
        project = Project()

        obj = CollectDataForIndicatorDashboard(project, None, None)
        self.assertEquals(obj.project, project)

    def test_that_indicator_type_is_set(self):
        indicator_type = 'Example Indicator type'
        obj = CollectDataForIndicatorDashboard(None, None, indicator_type)
        self.assertEquals(obj.indicator_type, indicator_type)

    def test_that_entity_is_null_when_entity_if_does_not_exist(self):
        entity_id = 42
        obj = CollectDataForIndicatorDashboard(None, entity_id, None)
        self.assertIsNone(obj.entity)

    def test_that_entity_is_fetched_from_db_the_given_entity_id_is_in_db(self):
        entity = EntityFactory.create()
        obj = CollectDataForIndicatorDashboard(None, entity.pk, None)
        self.assertEquals(obj.entity, entity)


class TestBuildResponse(TestCase):
    def setUp(self):
        # Dependency between QuestionnaireTemplate and ResearchMethodology
        questionnaire_template = QuestionnaireTemplateFactory.create()
        research_methodology = ResearchMethodologyFactory.create()
        research_methodology.questionnaires.add(questionnaire_template)

        self.question_template = QuestionTemplateFactory.create(questionnaire_template=questionnaire_template)

        # Dependency between Project and ResearchMethodology
        self.project = ProjectFactory.create(research_methodology=research_methodology)

        # Dependency between Project Evaluation and Questionnaire
        self.questionnaire1 = QuestionnaireFactory.create(template=questionnaire_template, title='first')
        self.evaluation1 = EvaluationFactory.create(project=self.project, questionnaire=self.questionnaire1)
        self.questionnaire2 = QuestionnaireFactory.create(template=questionnaire_template, title='second')
        self.evaluation2 = EvaluationFactory.create(project=self.project, questionnaire=self.questionnaire2)

    def _test_when_there_are_no_indicator_questions(self):
        indicator_type = fuzzy.FuzzyText(length=10)
        expected_result = {
            'details': [],
            'project_comment': [],
            'gauge': {
                'passives': None,
                'promoters': None,
                'indicator': None,
                'detractors': None
            },
            'coded_causes': []
        }
        result = CollectDataForIndicatorDashboard(self.project, None, indicator_type).build_response()
        self.assertDictEqual(result, expected_result)

    def test_when_there_are_two_indicator_questions_and_the_given_entity_is_none(self):
        indicator_type = 'random type'
        indicator_question = self._generate_first_indicator_question(indicator_type, 6)
        indicator_question = self._generate_second_indicator_question(indicator_type, 8)
        expected_result = {
            'details': [{
                'item_label': 'Entities',
                'results': [{
                    'score': {
                        'passives': 50.0,
                        'detractors': 50.0,
                        'promoters': 0.0,
                        'indicator': -50.0
                    },
                    'number_of_respondents': 2,
                    'choice': 'Aladeen',
                    'other_answer_choices': indicator_question.id
                }]
            }],
            'gauge': {
                'passives': 50.0,
                'detractors': 50.0,
                'promoters': 0.0,
                'indicator': -50.0
            },
            'coded_causes': [],
            'project_comment': None
        }
        self.maxDiff = None

        result = CollectDataForIndicatorDashboard(self.project, None, indicator_type).build_response()
        self.assertDictEqual(result, expected_result)

    def _generate_first_indicator_question(self, additional_info, score):
        block1 = QuestionnaireBlockFactory(questionnaire=self.questionnaire1)
        return IndicatorQuestionFactory.create(questionnaire=self.questionnaire1,
                                               block=block1,
                                               additional_info=additional_info,
                                               score=score,
                                               template_question=self.question_template)

    def _generate_second_indicator_question(self, additional_info, score):
        block2 = QuestionnaireBlockFactory(questionnaire=self.questionnaire2)
        return IndicatorQuestionFactory.create(questionnaire=self.questionnaire2,
                                               block=block2,
                                               additional_info=additional_info,
                                               score=score,
                                               template_question=self.question_template)

