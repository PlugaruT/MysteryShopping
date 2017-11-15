from django.test import TestCase

from mystery_shopping.common.iterators import pairs


class PairIteratorTestCase(TestCase):
    def test_empty_iterator(self):
        input_list = []

        output = list(pairs(input_list))
        self.assertListEqual(output, [])

    def test_one_element_with_last(self):
        input_list = [1]

        output = list(pairs(input_list))
        self.assertListEqual(output, [(1, None)])

    def test_one_element_without_last(self):
        input_list = [1]

        output = list(pairs(input_list, include_last=False))
        self.assertListEqual(output, [])

    def test_multiple_with_last(self):
        input_list = [1, 2, 3]

        output = list(pairs(input_list))
        self.assertListEqual(output, [(1, 2), (2, 3), (3, None)])

    def test_multiple_without_last(self):
        input_list = [1, 2, 3]

        output = list(pairs(input_list, include_last=False))
        self.assertListEqual(output, [(1, 2), (2, 3)])
