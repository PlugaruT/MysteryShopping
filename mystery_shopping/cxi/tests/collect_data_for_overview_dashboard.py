from django.test.testcases import TestCase

from mystery_shopping.cxi.algorithms import collect_data_for_overview_dashboard
from mystery_shopping.factories.companies import CompanyElementFactory
from mystery_shopping.factories.projects import ResearchMethodologyFactory, ProjectFactory, EvaluationFactory
from mystery_shopping.factories.questionnaires import QuestionnaireTemplateFactory, QuestionnaireFactory, \
    QuestionTemplateFactory, QuestionnaireBlockFactory, IndicatorQuestionFactory


class TestCollectDataForOverviewDashboard(TestCase):
    def setUp(self):
        # Dependency between QuestionnaireTemplate and ResearchMethodology
        self.questionnaire_template = QuestionnaireTemplateFactory.create()
        research_methodology = ResearchMethodologyFactory.create()
        research_methodology.questionnaires.add(self.questionnaire_template)

        self.indicator_type = 'random'

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

    def test_when_there_are_no_indicator_questions(self):
        expected_result = {
            'project_comment': None,
            'indicators': {}
        }
        result = collect_data_for_overview_dashboard(self.project, None, None, None)
        self.assertDictEqual(result, expected_result)

    def test_when_the_given_company_element_is_none_and_one_indicator_type(self):
        self._generate_first_indicator_question(self.indicator_type, 5, self.template_indicator_question)
        self._generate_second_indicator_question(self.indicator_type, 9, self.template_indicator_question)
        result = collect_data_for_overview_dashboard(self.project, None, None, None)
        expected_result = {
            'indicators': {
                'random': {
                    'promoters': 50.0,
                    'passives': 0.0,
                    'detractors': 50.0,
                    'indicator': 0.0
                }
            },
            'project_comment': None
        }
        self.assertDictEqual(result, expected_result)

    def test_when_the_given_company_element_is_none_and_two_different_indicator_types(self):
        indicator_type2 = 'another random'
        template_indicator_question2 = QuestionTemplateFactory.create(
            questionnaire_template=self.questionnaire_template, type='i', additional_info=indicator_type2)
        self._generate_first_indicator_question(self.indicator_type, 5, self.template_indicator_question)
        self._generate_second_indicator_question(indicator_type2, 9, template_indicator_question2)
        result = collect_data_for_overview_dashboard(self.project, None, None, None)
        expected_result = {
            'project_comment': None,
            'indicators': {
                'random': {
                    'detractors': 100.0,
                    'passives': 0.0,
                    'promoters': 0.0,
                    'indicator': -100.0
                },
                'another random': {
                    'detractors': 0.0,
                    'passives': 0.0,
                    'promoters': 100.0,
                    'indicator': 100.0
                }
            }
        }
        self.assertDictEqual(result, expected_result)

    def test_when_the_company_element_is_given(self):
        self._generate_first_indicator_question(self.indicator_type, 5, self.template_indicator_question)
        self._generate_second_indicator_question(self.indicator_type, 9, self.template_indicator_question)
        # change the company_element for second evaluation method to see the results just for on entity
        self.evaluation2.company_element = CompanyElementFactory()
        self.evaluation2.save()

        expected_result = {
            'indicators':
                {
                    'random':
                        {
                            'promoters': 0.0,
                            'indicator': -100.0,
                            'detractors': 100.0,
                            'passives': 0.0
                        }
                },
            'project_comment': None
        }

        result = collect_data_for_overview_dashboard(self.project, None, self.company_element.pk, None)
        self.assertDictEqual(result, expected_result)

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
