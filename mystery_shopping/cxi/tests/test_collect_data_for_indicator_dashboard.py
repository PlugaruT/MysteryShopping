from django.test.testcases import TestCase
from factory import fuzzy

from mystery_shopping.cxi.algorithms import CollectDataForIndicatorDashboard
from mystery_shopping.factories.companies import EntityFactory
from mystery_shopping.factories.projects import ResearchMethodologyFactory, ProjectFactory, EvaluationFactory
from mystery_shopping.factories.questionnaires import QuestionnaireTemplateFactory, QuestionnaireFactory, \
    IndicatorQuestionFactory, QuestionnaireBlockFactory, QuestionTemplateFactory, QuestionnaireTemplateQuestionChoiceFactory, \
    QuestionFactory, ChoiceFactory
from mystery_shopping.projects.constants import EvaluationStatus
from mystery_shopping.projects.models import Project


class TestClassConstructor(TestCase):
    def test_that_project_is_set(self):
        project = Project()

        obj = CollectDataForIndicatorDashboard(project, None, None, None, None)
        self.assertEqual(obj.project, project)

    def test_that_indicator_type_is_set(self):
        indicator_type = 'Example Indicator type'
        obj = CollectDataForIndicatorDashboard(None, None, None, None, indicator_type)
        self.assertEqual(obj.indicator_type, indicator_type)

    def test_that_entity_is_null_when_entity_if_does_not_exist(self):
        entity_id = 42
        obj = CollectDataForIndicatorDashboard(None, None, entity_id, None, None)
        self.assertIsNone(obj.entity)

    def test_that_entity_is_fetched_from_db_the_given_entity_id_is_in_db(self):
        entity = EntityFactory.create()
        obj = CollectDataForIndicatorDashboard(None, None, entity.pk, None, None)
        self.assertEqual(obj.entity, entity)


class TestBuildResponse(TestCase):
    def setUp(self):
        # Dependency between QuestionnaireTemplate and ResearchMethodology
        self.questionnaire_template = QuestionnaireTemplateFactory.create()
        research_methodology = ResearchMethodologyFactory.create()
        research_methodology.questionnaires.add(self.questionnaire_template)

        self.indicator_type = 'random'

        self.entity = EntityFactory.create()
        self.template_indicator_question = QuestionTemplateFactory.create(
            questionnaire_template=self.questionnaire_template, type='i', additional_info=self.indicator_type)

        # Dependency between Project and ResearchMethodology
        self.project = ProjectFactory.create(research_methodology=research_methodology)

        # Dependency between Project Evaluation and Questionnaire
        self.questionnaire1 = QuestionnaireFactory.create(template=self.questionnaire_template, title='first')
        self.evaluation1 = EvaluationFactory.create(project=self.project, questionnaire=self.questionnaire1,
                                                    entity=self.entity, status=EvaluationStatus.SUBMITTED)
        self.questionnaire2 = QuestionnaireFactory.create(template=self.questionnaire_template, title='second')
        self.evaluation2 = EvaluationFactory.create(project=self.project, questionnaire=self.questionnaire2,
                                                    entity=self.entity, status=EvaluationStatus.SUBMITTED)

    def test_when_there_are_no_indicator_questions(self):
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
        result = CollectDataForIndicatorDashboard(self.project, None, None, None, indicator_type).build_response()
        self.assertDictEqual(result, expected_result)

    def test_when_there_is_one_indicator_questions_and_the_given_entity_is_none(self):
        self._generate_first_indicator_question(self.indicator_type, 6, self.template_indicator_question)
        self._generate_second_indicator_question(self.indicator_type, 8, self.template_indicator_question)

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
                    'other_answer_choices': self.entity.id,
                    'choice_id': self.entity.id
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
        result = CollectDataForIndicatorDashboard(self.project, None, None, None, self.indicator_type).build_response()
        self.assertDictEqual(result, expected_result)

    def test_when_there_is_one_indicator_questions_and_entity_is_given(self):
        self.evaluation2.entity = EntityFactory(name='demo1')
        self.evaluation2.save()
        self._generate_first_indicator_question(self.indicator_type, 6, self.template_indicator_question)
        self._generate_second_indicator_question(self.indicator_type, 8, self.template_indicator_question)

        expected_result = {
            'gauge': {
                'detractors': 100.0,
                'promoters': 0.0,
                'passives': 0.0,
                'indicator': -100.0,
                'general_indicator': -50.0
            },
            'coded_causes': [],
            'details': [{
                'item_label': 'Entities',
                'results': [{
                    'score': {
                        'detractors': 100.0, 'promoters': 0.0,
                                                                          'passives': 0.0, 'indicator': -100.0},
                                                                'other_answer_choices': self.entity.id,
                                                                'choice_id': self.entity.id,
                                                                'number_of_respondents':
                                                                    1, 'choice': 'Aladeen'}]}], 'project_comment': None}

        self.maxDiff = None
        result = CollectDataForIndicatorDashboard(self.project, None, self.entity.id, None, self.indicator_type).build_response()
        self.assertDictEqual(expected_result, result)

    def test_when_there_is_one_indicator_questions_and_one_single_choice_question__and_the_given_entity_is_none(self):
        self._generate_first_indicator_question(self.indicator_type, 6, self.template_indicator_question)
        self._generate_second_indicator_question(self.indicator_type, 8, self.template_indicator_question)
        question_template = QuestionTemplateFactory(type='s', questionnaire_template=self.questionnaire_template,
                                                    question_body='question')
        question_template_choice1 = QuestionnaireTemplateQuestionChoiceFactory(text='choice 1',
                                                                               template_question=question_template)
        question_template_choice2 = QuestionnaireTemplateQuestionChoiceFactory(text='choice 2',
                                                                               template_question=question_template)

        block1 = QuestionnaireBlockFactory(questionnaire=self.questionnaire1)
        block2 = QuestionnaireBlockFactory(questionnaire=self.questionnaire2)
        question1 = QuestionFactory(type='s', question_body='question', template_question=question_template,
                                    questionnaire=self.questionnaire1, block=block1)
        question2 = QuestionFactory(type='s', question_body='question', template_question=question_template,
                                    questionnaire=self.questionnaire2, block=block2)

        choice_11 = ChoiceFactory(text='choice 1', question=question1, order=42)

        question1.answer = choice_11.text
        question1.answer_choices = [choice_11.id]

        choice_21 = ChoiceFactory(text='choice 1', question=question2, order=42)

        question2.answer = choice_21.text
        question2.answer_choices = [choice_21.id]

        question1.save()
        question2.save()

        expected_result = {
            'details': [{
                'item_label': 'question',
                'results': [
                    {
                        'score': {
                            'promoters': 0.0,
                            'detractors': 50.0,
                            'indicator': -50.0,
                            'passives': 50.0
                        },
                        'number_of_respondents': 2,
                        'order': 42,
                        'other_answer_choices': [],
                        'choice': question_template_choice1.text
                    },
                    {
                        'score': {
                            'promoters': None,
                            'detractors': None,
                            'indicator': None,
                            'passives': None,
                        },
                        'number_of_respondents': 0,
                        'order': 42,
                        'other_answer_choices': [],
                        'choice': question_template_choice2.text
                    }
                ]
            },
                {
                'item_label': 'Entities',
                'results': [
                    {
                        'score': {
                            'promoters': 0.0,
                            'detractors': 50.0,
                            'indicator': -50.0,
                            'passives': 50.0
                        },
                        'number_of_respondents': 2,
                        'other_answer_choices': self.entity.id,
                        'choice_id': self.entity.id,
                        'choice': 'Aladeen'
                    }
                ]
            }
            ],
            'project_comment': None,
            'coded_causes': [],
            'gauge': {
                'promoters': 0.0,
                'detractors': 50.0,
                'indicator': -50.0,
                'passives': 50.0
            }
        }
        result = CollectDataForIndicatorDashboard(self.project, None, None, None, self.indicator_type).build_response()
        self._order_result_lists_in_dict_for_indicator_dashboard(expected_result)
        self._order_result_lists_in_dict_for_indicator_dashboard(result)
        self.assertDictEqual(expected_result, result)

    def _generate_first_indicator_question(self, additional_info, score, question_template):
        block1 = QuestionnaireBlockFactory(questionnaire=self.questionnaire1)
        return IndicatorQuestionFactory.create(questionnaire=self.questionnaire1,
                                               block=block1,
                                               additional_info=additional_info,
                                               score=score,
                                               template_question=question_template, type='i')

    def _generate_second_indicator_question(self, additional_info, score, question_template):
        block2 = QuestionnaireBlockFactory(questionnaire=self.questionnaire2)
        return IndicatorQuestionFactory.create(questionnaire=self.questionnaire2,
                                               block=block2,
                                               additional_info=additional_info,
                                               score=score,
                                               template_question=question_template, type='i')

    def _order_result_lists_in_dict_for_indicator_dashboard(self, target):
        list_to_order = target.get('details')
        for detail in list_to_order:
            detail['results'] = self._order_detail(detail['results'])

    def _order_detail(self, detail):
        return sorted(detail, key=lambda k: k['choice'])
