from django.test.testcases import TestCase

from mystery_shopping.companies.utils import FilterCompanyStructure


class TestFilteringCompanyBasedOnPermissions(TestCase):
    def setUp(self):
        """
        define the following structure with the 'id' and 'childern' fields:
        1
        2
            3
            4
        5
            6
                7
                    8
                    9
                        10
        """
        self.node_10 = {
            'id': 10,
            'children': []
        }
        self.node_9 = {
            'id': 9,
            'children': [self.node_10]
        }
        self.node_8 = {
            'id': 8,
            'children': []
        }
        self.node_7 = {
            'id': 7,
            'children': [self.node_8, self.node_9]
        }
        self.node_6 = {
            'id': 6,
            'children': [self.node_7]
        }
        self.node_5 = {
            'id': 5,
            'children': [self.node_6]
        }
        self.node_4 = {
            'id': 4,
            'children': []
        }
        self.node_3 = {
            'id': 3,
            'children': []
        }
        self.node_2 = {
            'id': 2,
            'children': [self.node_3, self.node_4]
        }
        self.node_1 = {
            'id': 1,
            'children': []
        }

    def test_all_company_structure_is_allowed(self):
        """
        expected structure:
        1
        2
            3
            4
        5
            6
                7
                    8
                    9
                        10
        """
        nodes_list = [self.node_1, self.node_2, self.node_3, self.node_4, self.node_5,
                      self.node_6, self.node_7, self.node_8, self.node_9, self.node_10]
        allowed_nodes_id = [node['id'] for node in nodes_list]
        filtered_nodes = FilterCompanyStructure(nodes_list, allowed_nodes_id).run_filter()

        expected_result = [self.node_1, self.node_2, self.node_5]

        self.assertCountEqual(expected_result, filtered_nodes)

    def test_only_top_level_nodes_are_allowed(self):
        """
        expected structure:
        1
        2
        5
        """
        nodes_list = [self.node_1, self.node_2, self.node_5]
        allowed_nodes_id = [node['id'] for node in nodes_list]
        filtered_nodes = FilterCompanyStructure(nodes_list, allowed_nodes_id).run_filter()

        # modify nodes to the expected result
        self.node_1['children'] = []
        self.node_2['children'] = []
        self.node_5['children'] = []

        expected_result = [self.node_1, self.node_2, self.node_5]

        self.assertCountEqual(expected_result, filtered_nodes)

    def test_mixed_type_of_nodes_are_allowed(self):
        """
        expected structure:
        1
        2
            3
        5
        7
            9
                10
        """
        nodes_list = [self.node_1, self.node_2, self.node_3, self.node_5, self.node_7, self.node_9, self.node_10]
        allowed_nodes_id = [node['id'] for node in nodes_list]
        filtered_nodes = FilterCompanyStructure(nodes_list, allowed_nodes_id).run_filter()

        # modify nodes to the expected result
        self.node_1['children'] = []
        self.node_2['children'] = [self.node_3]
        self.node_5['children'] = []
        self.node_7['children'] = [self.node_9]
        self.node_9['children'] = [self.node_10]

        expected_result = [self.node_1, self.node_2, self.node_5, self.node_7]

        self.assertCountEqual(expected_result, filtered_nodes)
