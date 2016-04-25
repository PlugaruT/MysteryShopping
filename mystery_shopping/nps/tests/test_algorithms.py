from decimal import Decimal

from django.test import TestCase

from ..algorithms import calculate_indicator_score


class AlgorithmsTestCase(TestCase):
    def test_calculate_indicator_score_with_values(self):
        indicator_marks = [10, 9, 7, 6, 10, 9, 9, 8, 7, 7, 7, 10, 8, 3]
        # Transform them in to decimals because, the field that contains the nps value
        # is decimal
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
