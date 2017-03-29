from collections import defaultdict
from decimal import Decimal
from json import load
from random import randint
from unittest.mock import MagicMock, patch

from django.test import TestCase

from mystery_shopping.cxi.algorithms import calculate_cxi_scores
from mystery_shopping.factories.questionnaires import QuestionnaireTemplateStatusFactory, QuestionnaireTemplateFactory, \
    QuestionTemplateFactory, CustomWeightFactory
from mystery_shopping.factories.users import UserFactory
from mystery_shopping.questionnaires.models import CustomWeight
from ..algorithms import calculate_indicator_score
from ..algorithms import create_details_skeleton
from ..algorithms import get_indicator_scores
from ..algorithms import sort_indicator_question_marks
from ..algorithms import add_question_per_coded_cause
from ..algorithms import group_questions_by_answer
from ..algorithms import group_questions_by_pos
from ..algorithms import calculate_overview_score
from ..algorithms import sort_indicator_categories
from ..algorithms import sort_indicators_per_pos
from ..algorithms import sort_question_by_coded_cause

from mystery_shopping.questionnaires.serializers import QuestionnaireTemplateSerializer
from mystery_shopping.questionnaires.constants import QuestionType
from mystery_shopping.factories.tenants import TenantFactory
from mystery_shopping.factories.cxi import CodedCauseFactory, CodedCauseLabelFactory


class AlgorithmsTestCase(TestCase):
    def test_calculate_indicator_score_with_values_old_algorithm(self):
        indicator_marks = [10, 9, 7, 6, 10, 9, 9, 8, 7, 7, 7, 10, 8, 3]

        calculated_score = calculate_indicator_score(indicator_marks)

        self.assertEqual(calculated_score['promoters'], Decimal(43))
        self.assertEqual(calculated_score['detractors'], Decimal(14))
        self.assertEqual(calculated_score['passives'], Decimal(43))
        self.assertEqual(calculated_score['indicator'], Decimal(29))

    def test_calculate_indicator_score_without_values_old_algorithm(self):
        indicator_marks = list()

        calculated_score = calculate_indicator_score(indicator_marks)

        self.assertEqual(calculated_score['promoters'], None)
        self.assertEqual(calculated_score['detractors'], None)
        self.assertEqual(calculated_score['passives'], None)
        self.assertEqual(calculated_score['indicator'], None)

    def test_calculate_indicator_score_with_values_new_algorithm(self):
        indicator_marks = [10, 9, 7, 6, 10, 9, 9, 8, 7, 7, 7, 10, 8, 3]
        # calculated by hand
        expected_result = 69  # non intentional :)

        calculated_score = calculate_indicator_score(indicator_marks=indicator_marks, new_algorithm=True)

        self.assertEqual(calculated_score['indicator'], Decimal(expected_result))

    def test_calculate_indicator_score_without_values_new_algorithm(self):
        indicator_marks = list()

        calculated_score = calculate_indicator_score(indicator_marks=indicator_marks, new_algorithm=True)

        self.assertEqual(calculated_score['indicator'], None)

    def test_cxi_weights_with_all_new_algorithm_indicators(self):
        indicator_name_1 = 'name1'
        indicator_name_2 = 'name2'
        template_questionnaire = QuestionnaireTemplateFactory()
        question_1 = QuestionTemplateFactory(questionnaire_template=template_questionnaire,
                                             type=QuestionType.INDICATOR_QUESTION, additional_info=indicator_name_1)
        question_2 = QuestionTemplateFactory(questionnaire_template=template_questionnaire,
                                             type=QuestionType.INDICATOR_QUESTION, additional_info=indicator_name_2)

        custom_weight_name_1 = 'Weight-1'
        custom_weight_name_2 = 'Weight-2'
        CustomWeightFactory(question=question_1, name=custom_weight_name_1, weight=40)
        CustomWeightFactory(question=question_1, name=custom_weight_name_2, weight=50)

        CustomWeightFactory(question=question_2, name=custom_weight_name_1, weight=60)
        CustomWeightFactory(question=question_2, name=custom_weight_name_2, weight=50)

        indicator_scores = {
            indicator_name_1: {
                'indicator': Decimal(75)
            },
            indicator_name_2: {
                'indicator': Decimal(60)
            }
        }
        result = calculate_cxi_scores(indicator_scores, {}, template_questionnaire)

        result_indicator_1 = Decimal(66)
        result_indicator_2 = Decimal(68)
        self.assertEqual(result[custom_weight_name_1], result_indicator_1)
        self.assertEqual(result[custom_weight_name_2], result_indicator_2)

    def test_cxi_weights_with_new_and_old_algorithm_indicators(self):
        indicator_name_1 = 'name1'
        indicator_name_2 = 'name2'
        template_questionnaire = QuestionnaireTemplateFactory()
        question_1 = QuestionTemplateFactory(questionnaire_template=template_questionnaire,
                                             type=QuestionType.INDICATOR_QUESTION, additional_info=indicator_name_1,
                                             new_algorithm=False)
        question_2 = QuestionTemplateFactory(questionnaire_template=template_questionnaire,
                                             type=QuestionType.INDICATOR_QUESTION, additional_info=indicator_name_2)

        custom_weight_name_1 = 'Weight-1'
        custom_weight_name_2 = 'Weight-2'
        CustomWeightFactory(question=question_1, name=custom_weight_name_1, weight=40)
        CustomWeightFactory(question=question_1, name=custom_weight_name_2, weight=50)

        CustomWeightFactory(question=question_2, name=custom_weight_name_1, weight=60)
        CustomWeightFactory(question=question_2, name=custom_weight_name_2, weight=50)

        indicator_scores = {
            indicator_name_1: {
                'indicator': 75
            },
            indicator_name_2: {
                'indicator': 60
            }
        }

        old_algorithm_indicator_dict = {
            indicator_name_1: [Decimal(10), Decimal(10), Decimal(2)]
        }
        result = calculate_cxi_scores(indicator_scores, old_algorithm_indicator_dict, template_questionnaire)

        result_indicator_1 = Decimal(61)
        result_indicator_2 = Decimal(62)
        self.assertEqual(result[custom_weight_name_1], result_indicator_1)
        self.assertEqual(result[custom_weight_name_2], result_indicator_2)

    def test_get_indicator_scores_with_some_return_elements(self):
        initial_score_list = [Decimal('8.00'), Decimal('6.00'), Decimal('10.00'), Decimal('6.00'), Decimal('5.00')]
        questionnaire_list = list()
        indicator_type_1 = 'NPS'
        indicator_type_2 = 'Enjoyability'

        # Create the mocks for the questionnaires
        for index in range(len(initial_score_list) - 1):
            questionnaire = MagicMock()
            mock_question = MagicMock()
            mock_question.type = QuestionType.INDICATOR_QUESTION
            mock_question.additional_info = indicator_type_1
            mock_question.score = initial_score_list[index]
            # Assign questions to the questionnaire
            questionnaire.questions_list = [mock_question, ]
            questionnaire_list.append(questionnaire)

        # Add another questionnaire with a different type of cxi question
        questionnaire_list.append(MagicMock())
        mock_question = MagicMock()
        mock_question.type = QuestionType.INDICATOR_QUESTION
        mock_question.additional_info = indicator_type_2
        mock_question.score = initial_score_list[-1]
        questionnaire_list[-1].questions.all.return_value = [mock_question, ]

        return_score_list = get_indicator_scores(questionnaire_list, indicator_type_1)

        self.assertEqual(initial_score_list[:-1], return_score_list)

    def test_get_indicator_scores_with_no_elements(self):
        initial_score_list = [Decimal('8.00'), Decimal('6.00'), Decimal('10.00'), Decimal('6.00'), Decimal('5.00')]
        questionnaire_list = list()
        indicator_type_1 = 'NPS'
        indicator_type_2 = 'Enjoyability'

        # Create the mocks for the questionnaires
        for index in range(len(initial_score_list) - 1):
            questionnaire = MagicMock()
            mock_question = MagicMock()
            mock_question.type = QuestionType.INDICATOR_QUESTION
            mock_question.additional_info = indicator_type_1
            mock_question.score = initial_score_list[index]
            # Assign questions to the questionnaire
            questionnaire.questions_list = [mock_question, ]
            questionnaire_list.append(questionnaire)

        return_score_list = get_indicator_scores(questionnaire_list, indicator_type_2)

        self.assertEqual(list(), return_score_list)

    def test_create_details_skeleton(self):
        # populate the test skeleton with the expected keys
        test_indicator_skeleton = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        test_indicator_skeleton['Language'] = defaultdict()
        test_indicator_skeleton['Language']['Romanian'] = defaultdict()
        test_indicator_skeleton['Language']['English'] = defaultdict()

        test_indicator_skeleton['Age'] = defaultdict()
        test_indicator_skeleton['Age']['14-18'] = defaultdict()
        test_indicator_skeleton['Age']['19-25'] = defaultdict()
        test_indicator_skeleton['Age']['26-100'] = defaultdict()

        test_indicator_skeleton['Gender'] = defaultdict()
        test_indicator_skeleton['Gender']['Male'] = defaultdict()
        test_indicator_skeleton['Gender']['Female'] = defaultdict()

        for big_key in test_indicator_skeleton:
            for small_key in test_indicator_skeleton[big_key]:
                test_indicator_skeleton[big_key][small_key]['marks'] = []
                test_indicator_skeleton[big_key][small_key]['order'] = 0
                test_indicator_skeleton[big_key][small_key]['other_choices'] = []

        # create a template questionnaire
        data = load(open("mystery_shopping/cxi/tests/template_questionnaire_for_skeleton.json"))
        tenant = TenantFactory()
        created_by = UserFactory()
        status = QuestionnaireTemplateStatusFactory()
        data['created_by'] = created_by.id
        data['status'] = status.id
        data['tenant'] = tenant.id
        template_ser = QuestionnaireTemplateSerializer(data=data)
        template_ser.is_valid(raise_exception=True)
        template_ser.save()

        indicator_skeleton = create_details_skeleton(template_ser.instance)

        # Check the "outer" keys
        if test_indicator_skeleton.keys() == indicator_skeleton.keys():
            pass
        else:
            self.assertTrue(False)

        # check whether the keys match
        for big_key in indicator_skeleton:
            for medium_key in indicator_skeleton[big_key]:
                self.assertIn(medium_key, test_indicator_skeleton[big_key])
                for small_key in indicator_skeleton[big_key][medium_key]:
                    self.assertIn(small_key, test_indicator_skeleton[big_key][medium_key])

    def test_sort_indicator_question_marks_with_answer_choices(self):
        indicator_dict = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        mark = Decimal(10.00)
        answer_choice = 123

        indicator_question = MagicMock()
        indicator_question.type = QuestionType.INDICATOR_QUESTION
        indicator_question.score = mark

        question = MagicMock()
        question.type = QuestionType.SINGLE_CHOICE
        question.answer = 'Romanian'
        question.question_body = 'Language'
        question.answer_choices = answer_choice

        sort_indicator_question_marks(indicator_dict, indicator_question, question)

        self.assertEqual(indicator_dict[question.question_body][question.answer]['marks'][0], mark)

    def test_sort_indicator_question_marks_with_no_answer_choices(self):
        indicator_dict = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        mark = Decimal(10.00)
        answer_choice = []

        indicator_question = MagicMock()
        indicator_question.type = QuestionType.INDICATOR_QUESTION
        indicator_question.score = mark

        question = MagicMock()
        question.type = QuestionType.SINGLE_CHOICE
        question.answer = 'Romanian'
        question.question_body = 'Language'
        question.answer_choices = answer_choice

        sort_indicator_question_marks(indicator_dict, indicator_question, question)

        self.assertEqual(indicator_dict[question.question_body]['other']['marks'][0], mark)

    def test_sort_indicator_question_marks_with_with_indicator_question(self):
        indicator_dict = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        mark = Decimal(10.00)
        answer_choice = []

        indicator_question = MagicMock()
        indicator_question.type = QuestionType.INDICATOR_QUESTION
        indicator_question.score = mark

        question = MagicMock()
        question.type = QuestionType.INDICATOR_QUESTION
        question.answer = 'lalala'
        question.question_body = 'NPS'
        question.answer_choices = answer_choice

        sort_indicator_question_marks(indicator_dict, indicator_question, question)

        self.assertFalse(indicator_dict[question.question_body]['other']['marks'])

    def test_add_question_per_coded_cause_with_cc(self):
        coded_causes_dict = defaultdict(list)

        cc_id = randint(1, 100)
        coded_cause = MagicMock()
        coded_cause.id = cc_id
        why_cause = MagicMock()

        indicator_question_id = randint(1, 100)
        indicator_question = MagicMock()
        indicator_question.id = indicator_question_id
        indicator_question.why_causes_list = [why_cause]
        why_cause.coded_causes_list = [coded_cause]

        add_question_per_coded_cause(indicator_question, coded_causes_dict)
        self.assertEqual(coded_causes_dict[coded_cause.id][0], indicator_question_id)

    def test_group_questions_by_answer(self):
        questionnaire_list = list()
        indicator_type = 'NPS'
        number_of_questionnaires = 5
        indicator_marks = list()

        for q in range(number_of_questionnaires):
            mark = randint(1, 10)
            indicator_marks.append(mark)
            question_list = list()
            question = MagicMock()
            questionnaire = MagicMock()
            indicator_question = MagicMock()

            indicator_question_id = randint(1, 100)
            indicator_question.type = QuestionType.INDICATOR_QUESTION
            indicator_question.score = mark
            indicator_question.id = indicator_question_id
            indicator_question.additional_info = indicator_type
            indicator_question.coded_causes_list = []

            question.type = QuestionType.SINGLE_CHOICE
            if q < 2:
                question.answer = 'Romanian'
                question.answer_choices = [123]
            elif q < 4:
                question.answer = 'English'
                question.answer_choices = [123]
            else:
                question.answer = 'Chinese'
                question.answer_choices = []

            question.question_body = 'Language'

            question_list.append(question)
            question_list.append(indicator_question)

            questionnaire.questions_list = question_list
            questionnaire_list.append(questionnaire)

        indicator_details = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

        group_questions_by_answer(questionnaire_list, indicator_type, indicator_details)

        self.assertEqual(indicator_details['Language']['Romanian']['marks'], indicator_marks[0:2])
        self.assertEqual(indicator_details['Language']['English']['marks'], indicator_marks[2:4])
        self.assertEqual(indicator_details['Language']['other']['marks'], indicator_marks[4:])

    def test_group_questions_by_pos(self):
        questionnaire_list = list()
        indicator_type = 'NPS'
        number_of_questionnaires = 5
        indicator_marks = list()

        company_element_1 = MagicMock()
        company_element_1.element_name = 'Entity 1'
        company_element_2 = MagicMock()
        company_element_2.element_name = 'Entity 2'

        for q in range(number_of_questionnaires):
            mark = randint(0, 10)
            indicator_marks.append(mark)
            questionnaire = MagicMock()
            indicator_question = MagicMock()

            indicator_question.type = QuestionType.INDICATOR_QUESTION
            indicator_question.score = mark
            indicator_question.additional_info = indicator_type

            questionnaire.questions_list = [indicator_question]

            questionnaire.evaluation.section = None

            if q < 3:
                questionnaire.get_company_element.return_value = company_element_1
            else:
                questionnaire.get_company_element.return_value = company_element_2

            questionnaire_list.append(questionnaire)

        indicator_pos_details = group_questions_by_pos(questionnaire_list, indicator_type)
        self.assertEqual(indicator_pos_details['entities'][company_element_1.element_name], indicator_marks[:3])
        self.assertEqual(indicator_pos_details['entities'][company_element_2.element_name], indicator_marks[3:])

    def _test_calculate_overview_score(self):
        initial_score_list = [Decimal('10.00'), Decimal('9.00'), Decimal('10.00'), Decimal('6.00'), Decimal('7.00')]
        promoters = Decimal('60.0')
        passives = Decimal('20.0')
        detractors = Decimal('20.0')
        indicator = Decimal('40.0')

        questionnaire_list = list()
        first_indicator = 'First Indicator'
        second_indicator = 'Second Indicator'

        # Create the questionnaire mocks with indicator questions
        for i in range(len(initial_score_list)):
            questionnaire = MagicMock()
            indicator_question_1 = MagicMock()
            indicator_question_1.type = QuestionType.INDICATOR_QUESTION
            indicator_question_1.additional_info = first_indicator
            indicator_question_1.order = 1
            indicator_question_1.score = initial_score_list[i]

            indicator_question_2 = MagicMock()
            indicator_question_2.type = QuestionType.INDICATOR_QUESTION
            indicator_question_2.additional_info = second_indicator
            indicator_question_2.order = 2
            indicator_question_2.score = initial_score_list[i]
            # Assign questions to the questionnaire
            questionnaire.get_indicator_questions.return_value = [indicator_question_1, indicator_question_2]
            questionnaire.questions_list = [indicator_question_1, indicator_question_2]

            questionnaire_list.append(questionnaire)

        overview_list = calculate_overview_score(questionnaire_list, None, None)
        self.assertEqual(overview_list['indicators'][first_indicator]['promoters'], promoters)
        self.assertEqual(overview_list['indicators'][first_indicator]['detractors'], detractors)
        self.assertEqual(overview_list['indicators'][first_indicator]['passives'], passives)
        self.assertEqual(overview_list['indicators'][first_indicator]['indicator'], indicator)

    # TODO: improve this test
    def test_sort_indicator_categories(self):
        initial_score_list = [Decimal('10.00'), Decimal('9.00'), Decimal('10.00'), Decimal('6.00'), Decimal('7.00')]
        new_algorithm = False

        indicator_categories = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        questions_dict = {'Age': ('10', '20', '30'), 'Gender': ('Male', 'Female')}

        for question, answers in questions_dict.items():
            for answer in answers:
                indicator_categories[question][answer]['marks'] = initial_score_list

        details = list()

        sort_indicator_categories(details, indicator_categories, new_algorithm)
        for question in details:
            for result in question['results']:
                self.assertEqual(result['number_of_respondents'], len(initial_score_list))
                self.assertEqual(result['score']['indicator'], 40.0)

    # TODO: improve this test
    def test_sort_indicators_per_pos_old_algorithm(self):
        new_algorithm = False
        initial_score_list = [Decimal('10.00'), Decimal('9.00'), Decimal('10.00'), Decimal('6.00'), Decimal('7.00')]

        indicator_pos_details = defaultdict(lambda: defaultdict(list))
        pos_list = ('Europe', 'Asia', 'Africa')

        for pos in pos_list:
            indicator_pos_details['entities'][pos] = initial_score_list

        details = list()
        sort_indicators_per_pos(details, indicator_pos_details, new_algorithm)
        for pos in details:
            for result in pos['results']:
                self.assertEqual(result['number_of_respondents'], len(initial_score_list))
                self.assertEqual(result['score']['indicator'], 40.0)

    def test_sort_question_by_coded_cause(self):
        coded_causes_dict = defaultdict(list)

        coded_cause_1 = CodedCauseFactory(type="a")
        coded_cause_2 = CodedCauseFactory(type="b")
        coded_cause_3 = CodedCauseFactory(type="c")

        indicator_question_1 = MagicMock()
        indicator_question_1.id = 11
        coded_causes_dict[coded_cause_1.id].append(indicator_question_1.id)

        indicator_question_2 = MagicMock()
        indicator_question_2.id = 22
        coded_causes_dict[coded_cause_1.id].append(indicator_question_2.id)

        indicator_question_3 = MagicMock()
        indicator_question_3.id = 33
        coded_causes_dict[coded_cause_2.id].append(indicator_question_3.id)

        indicator_question_4 = MagicMock()
        indicator_question_4.id = 44
        coded_causes_dict[coded_cause_3.id].append(indicator_question_4.id)

        result = sort_question_by_coded_cause(coded_causes_dict, 4)

        expected_result = [
            {
                'count': 2,
                'coded_cause': {
                    'coded_label': {},
                    'tenant': coded_cause_1.tenant.id,
                    'type': 'a',
                    'id': coded_cause_1.id,
                    'project': coded_cause_1.project.id,
                    'sentiment': coded_cause_1.sentiment,
                    'parent': None
                }
            },
            {
                'count': 1,
                'coded_cause': {
                    'coded_label': {},
                    'tenant': coded_cause_2.tenant.id,
                    'type': 'b',
                    'id': coded_cause_2.id,
                    'project': coded_cause_2.project.id,
                    'sentiment': coded_cause_2.sentiment,
                    'parent': None
                }
            },
            {
                'count': 1,
                'coded_cause': {
                    'coded_label': {},
                    'tenant': coded_cause_3.tenant.id,
                    'type': 'c',
                    'id': coded_cause_3.id,
                    'project': coded_cause_3.project.id,
                    'sentiment': coded_cause_3.sentiment,
                    'parent': None
                }
            }
        ]

        for item in result:
            print(item)
            item['coded_cause']['coded_label'] = {}
            item['coded_cause'].pop('why_causes_count')
            item['coded_cause'].pop('why_causes')
            item.pop('percentage')

        self.assertCountEqual(expected_result, result)
