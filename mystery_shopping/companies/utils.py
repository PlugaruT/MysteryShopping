from operator import itemgetter


class FilterCompanyStructure:
    """
    Class that filters company children based on the allowed ones
    """
    def __init__(self, nodes_list, allowed_entity_ids):
        """
        :param nodes_list: list of serialized nodes with all their children
        :param allowed_entity_ids: list of the ids of the entities the user has permission to access
        """
        self.nodes_list = nodes_list
        self.allowed_entity_ids = allowed_entity_ids

    def run_filter(self):
        """
        run this and all your dreams will be fulfilled

        :return: returns the minimal list of serialized entities and their allowed children
        """
        self._exclude_not_allowed_entities(self.nodes_list)
        self._sort_nodes_by_depth()
        return self._get_accepted_nodes()

    def _exclude_not_allowed_entities(self, nodes_list):
        """
        Exclude child entities if they are not allowed

        :param parent: list of fully serialized allowed_entities
        :return: a list of all possible allowed entities with "allowed" children
        """
        for parent in nodes_list:
            for child in parent['children']:
                if child['id'] not in self.allowed_entity_ids:
                    parent['children'].remove(child)

            self._exclude_not_allowed_entities(parent['children'])

    def _sort_nodes_by_depth(self):
        """
        method that adds the 'depth' key to the node with denotes the
        level of his deepest child
        """
        for node in self.nodes_list:
            node['depth'] = self._find_depth(node, 0)

        self.nodes_list = sorted(self.nodes_list, key=itemgetter('depth'), reverse=True)

    def _find_depth(self, node, parent_depth):
        """
        recursive method that finds the deepest level of the node

        :param node: elemnt to search the depth
        :param parent_depth: the depth that is sent (recursively) for the previous level
        :return: the maximum death of the node's children
        """
        if len(node['children']) == 0:
            return parent_depth

        children_depths = []
        for child in node['children']:
            children_depths.append(self._find_depth(child, parent_depth + 1))

        return max(children_depths)

    def _get_descendants(self, node):
        """
        method to recursively find the ids of all of the node's children

        :param node: element to find the descendants' ids
        :return: list of descendants' ids
        """
        descendants = list()
        def find_children(node):
            """
            recursive method to find the node's children

            :param node: node to find children for
                (NOTE: this node is not necessarily the node from the outer method)
            """
            for child in node['children']:
                descendants.append(child['id'])
                find_children(child)

        find_children(node)

        return descendants

    def _get_accepted_nodes(self):
        """
        method to filter out top level nodes that are found in lower levels

        initial structure:
            10
                33
                16
                    11
                        2
                    20
            16
                11
                    2
                20
            11
                2
            23
                15
            33
            21
                35
            2
            20
            15
            35
            45

        filtered structure:
            10
                33
                16
                    11
                        2
                    20
            23
                15
            21
                35
            45
        :return: list of nodes with the filtered structure
        """
        accepted_nodes = list()
        visited = set()

        for node in self.nodes_list:
            if not node['id'] in visited:
                visited.add(node['id'])
                descendants = self._get_descendants(node)
                visited = visited.union(descendants)
                accepted_nodes.append(node)

        return accepted_nodes
