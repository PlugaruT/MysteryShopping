from collections import defaultdict
from decimal import Decimal
from json import load
from random import randint
from unittest.mock import MagicMock

from django.test import TestCase

from ..algorithms import calculate_indicator_score
from ..algorithms import create_details_skeleton
from ..algorithms import get_indicator_scores
from ..algorithms import sort_indicator_question_marks
from ..algorithms import add_question_per_coded_cause

from mystery_shopping.questionnaires.serializers import QuestionnaireTemplateSerializer
from mystery_shopping.questionnaires.constants import IndicatorQuestionType
from mystery_shopping.questionnaires.constants import QuestionType
from mystery_shopping.factories.tenants import TenantFactory


class AlgorithmsTestCase(TestCase):
    def test_calculate_indicator_score_with_values(self):
        indicator_marks = [10, 9, 7, 6, 10, 9, 9, 8, 7, 7, 7, 10, 8, 3]
        # Transform them in to decimals because, the field that
        # contains the nps value is decimal
        for index, value in enumerate(indicator_marks):
            value = Decimal(value)

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
            questionnaire_list.append(MagicMock())
            mock_question = MagicMock()
            mock_question.type = IndicatorQuestionType.INDICATOR_QUESTION
            mock_question.additional_info = indicator_type
            mock_question.score = initial_score_list[i]
            # Assign questions to the questionnaire
            questionnaire_list[i].questions.all.return_value = [mock_question,]

        # Add another questionnaire with a different type of cxi question
        questionnaire_list.append(MagicMock())
        mock_question = MagicMock()
        mock_question.type = IndicatorQuestionType.INDICATOR_QUESTION
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
                test_indicator_skeleton[big_key][small_key]['other_choices'] = []

        # create a template questionnaire
        data = load(open("mystery_shopping/nps/tests/template_questionnaire_for_skeleton.json"))
        tenant = TenantFactory()
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
        indicator_question.type = IndicatorQuestionType.INDICATOR_QUESTION
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
        indicator_question.type = IndicatorQuestionType.INDICATOR_QUESTION
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
        indicator_question.type = IndicatorQuestionType.INDICATOR_QUESTION
        indicator_question.score = mark

        question = MagicMock()
        question.type = IndicatorQuestionType.INDICATOR_QUESTION
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

        indicator_question_id = randint(1, 100)
        indicator_question = MagicMock()
        indicator_question.id = indicator_question_id
        indicator_question.coded_causes.first.return_value = coded_cause

        add_question_per_coded_cause(indicator_question, coded_causes_dict)
        self.assertEqual(coded_causes_dict[coded_cause.id][0], indicator_question_id)

    def test_add_question_per_coded_cause_without_cc(self):
        coded_causes_dict = defaultdict(list)

        indicator_question_id = randint(1, 100)
        indicator_question = MagicMock()
        indicator_question.id = indicator_question_id
        indicator_question.coded_causes.first.return_value = None

        add_question_per_coded_cause(indicator_question, coded_causes_dict)
        self.assertEqual(coded_causes_dict['unsorted'][0], indicator_question_id)
