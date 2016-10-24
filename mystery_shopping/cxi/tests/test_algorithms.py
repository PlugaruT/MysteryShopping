from collections import defaultdict
from decimal import Decimal
from json import load
from random import randint
from unittest.mock import MagicMock

from django.test import TestCase

from mystery_shopping.factories.questionnaires import QuestionnaireTemplateStatusFactory
from mystery_shopping.factories.users import UserFactory
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
    def test_calculate_indicator_score_with_values(self):
        indicator_marks = [10, 9, 7, 6, 10, 9, 9, 8, 7, 7, 7, 10, 8, 3]
        # Transform them in to decimals because, the field that
        # contains the cxi value is decimal
        for index, value in enumerate(indicator_marks):
            value = Decimal(value)
        # print(indicator_marks)
        # indicator_marks = [Decimal(value) for value in indicator_marks]
        # print(indicator_marks)

        calculated_score = calculate_indicator_score(indicator_marks)

        self.assertEqual(calculated_score['promoters'], Decimal(42.86))
        self.assertEqual(calculated_score['detractors'], Decimal(14.29))
        self.assertEqual(calculated_score['passives'], Decimal(42.86))
        self.assertEqual(calculated_score['indicator'], Decimal(28.57))

    def test_calculate_indicator_score_without_values(self):
        indicator_marks = list()

        calculated_score = calculate_indicator_score(indicator_marks)

        self.assertEqual(calculated_score['promoters'], None)
        self.assertEqual(calculated_score['detractors'], None)
        self.assertEqual(calculated_score['passives'], None)
        self.assertEqual(calculated_score['indicator'], None)

    def test_get_indicator_scores_with_some_return_elements(self):
        initial_score_list = [Decimal('8.00'), Decimal('6.00'), Decimal('10.00'), Decimal('6.00'), Decimal('5.00')]
        questionnaire_list = list()
        indicator_type = 'NPS'

        # Create the mocks for the questionnaires
        for i in range(len(initial_score_list) - 1):
            questionnaire = MagicMock()
            mock_question = MagicMock()
            mock_question.type = QuestionType.INDICATOR_QUESTION
            mock_question.additional_info = indicator_type
            mock_question.score = initial_score_list[i]
            # Assign questions to the questionnaire
            questionnaire.questions.all.return_value = [mock_question,]
            questionnaire_list.append(questionnaire)

        # Add another questionnaire with a different type of cxi question
        questionnaire_list.append(MagicMock())
        mock_question = MagicMock()
        mock_question.type = QuestionType.INDICATOR_QUESTION
        mock_question.additional_info = 'Enjoyability'
        mock_question.score = initial_score_list[-1]
        questionnaire_list[-1].questions.all.return_value = [mock_question,]

        return_score_list = get_indicator_scores(questionnaire_list, indicator_type)

        self.assertEqual(initial_score_list[:-1], return_score_list)

    def test_get_indicator_scores_with_some_no_elements(self):
        initial_score_list = [Decimal('8.00'), Decimal('6.00'), Decimal('10.00'), Decimal('6.00'), Decimal('5.00')]
        questionnaire_list = list()
        indicator = 'n'

        # Create the mocks for the questionnaires
        for i in range(len(initial_score_list)):
            questionnaire_list.append(MagicMock())
            mock_question = MagicMock()
            mock_question.type = 'j'
            mock_question.score = initial_score_list[i]
            # Assign questions to the questionnaire
            questionnaire_list[i].questions.all.return_value = [mock_question,]

        return_score_list = get_indicator_scores(questionnaire_list, indicator)

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
        indicator_question.why_causes.all.return_value = [why_cause]
        why_cause.coded_causes.first.return_value = coded_cause

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
            indicator_question.coded_causes.first.return_value = None

            questionnaire.questions.filter().first.return_value = indicator_question

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

            questionnaire.questions.all.return_value = question_list
            questionnaire_list.append(questionnaire)

        indicator_details = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

        group_questions_by_answer(questionnaire_list, indicator_type, indicator_details)

        self.assertEqual(indicator_details['Language']['Romanian']['marks'], indicator_marks[0:2])
        self.assertEqual(indicator_details['Language']['English']['marks'], indicator_marks[2:4])
        self.assertEqual(indicator_details['Language']['other']['marks'], indicator_marks[4:])

    def test_group_questions_by_pos_with_no_sections(self):
        questionnaire_list = list()
        indicator_type = 'NPS'
        number_of_questionnaires = 5
        indicator_marks = list()

        for q in range(number_of_questionnaires):
            mark = randint(1, 10)
            indicator_marks.append(mark)
            questionnaire = MagicMock()
            indicator_question = MagicMock()

            indicator_question.type = QuestionType.INDICATOR_QUESTION
            indicator_question.score = mark
            indicator_question.additional_info = indicator_type

            questionnaire.questions.filter().first.return_value = indicator_question

            questionnaire.evaluation.section = None

            if q < 3:
                questionnaire.evaluation.entity.name = 'Entity 1'
            else:
                questionnaire.evaluation.entity.name = 'Entity 2'

            questionnaire_list.append(questionnaire)

        indicator_pos_details = group_questions_by_pos(questionnaire_list, indicator_type)
        self.assertEqual(indicator_pos_details['entities']['Entity 1'], indicator_marks[:3])
        self.assertEqual(indicator_pos_details['entities']['Entity 2'], indicator_marks[3:])

    def test_calculate_overview_score(self):
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
            indicator_question_1.score = initial_score_list[i]

            indicator_question_2 = MagicMock()
            indicator_question_2.type = QuestionType.INDICATOR_QUESTION
            indicator_question_2.additional_info = second_indicator
            indicator_question_2.score = initial_score_list[i]
            # Assign questions to the questionnaire
            questionnaire.questions.filter().all.return_value = [indicator_question_1, indicator_question_2]
            questionnaire.questions.all.return_value = [indicator_question_1, indicator_question_2]

            questionnaire_list.append(questionnaire)

        overview_list = calculate_overview_score(questionnaire_list, None, None, None, None)
        self.assertEqual(overview_list['indicators'][first_indicator]['promoters'], promoters)
        self.assertEqual(overview_list['indicators'][first_indicator]['detractors'], detractors)
        self.assertEqual(overview_list['indicators'][first_indicator]['passives'], passives)
        self.assertEqual(overview_list['indicators'][first_indicator]['indicator'], indicator)

    # TODO: improve this test
    def test_sort_indicator_categories(self):
        initial_score_list = [Decimal('10.00'), Decimal('9.00'), Decimal('10.00'), Decimal('6.00'), Decimal('7.00')]

        indicator_categories = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        questions_dict = {'Age': ('10', '20', '30'), 'Gender': ('Male', 'Female')}

        for question, answers in questions_dict.items():
            for answer in answers:
                indicator_categories[question][answer]['marks'] = initial_score_list

        details = list()

        sort_indicator_categories(details, indicator_categories)
        for question in details:
            for result in question['results']:
                self.assertEqual(result['number_of_respondents'], len(initial_score_list))
                self.assertEqual(result['score']['indicator'], 40.0)

    # TODO: improve this test
    def test_sort_indicators_per_pos(self):
        initial_score_list = [Decimal('10.00'), Decimal('9.00'), Decimal('10.00'), Decimal('6.00'), Decimal('7.00')]

        indicator_pos_details = defaultdict(lambda: defaultdict(list))
        pos_list = ('Europe', 'Asia', 'Africa')

        for pos in pos_list:
            indicator_pos_details['entities'][pos] = initial_score_list

        details = list()
        sort_indicators_per_pos(details, indicator_pos_details)
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

        result = sort_question_by_coded_cause(coded_causes_dict)

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

        self.maxDiff = None

        for item in result:
            item['coded_cause']['coded_label'] = {}

        print(result)

        self.assertCountEqual(expected_result, result)
