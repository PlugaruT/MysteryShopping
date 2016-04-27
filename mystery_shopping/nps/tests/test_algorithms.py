from decimal import Decimal
from unittest.mock import MagicMock

from django.test import TestCase

from ..algorithms import calculate_indicator_score
from ..algorithms import get_indicator_scores


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
        indicator = 'n'

        # Create the mocks for the questionnaires
        for i in range(len(initial_score_list) - 1):
            questionnaire_list.append(MagicMock())
            mock_question = MagicMock()
            mock_question.type = indicator
            mock_question.score = initial_score_list[i]
            # Assign questions to the questionnaire
            questionnaire_list[i].questions.all.return_value = [mock_question,]

        # Add another questionnaire with a different type of cxi question
        questionnaire_list.append(MagicMock())
        mock_question = MagicMock()
        mock_question.type = 'j'
        mock_question.score = initial_score_list[-1]
        questionnaire_list[-1].questions.all.return_value = [mock_question,]

        return_score_list = get_indicator_scores(questionnaire_list, indicator)

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
