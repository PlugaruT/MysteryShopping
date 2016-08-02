from django.test.testcases import TestCase

from mystery_shopping.cxi.algorithms import CollectDataForIndicatorDashboard
from mystery_shopping.factories.companies import EntityFactory
from mystery_shopping.projects.models import Project


class TestClassConstructor(TestCase):
    def test_that_project_is_set(self):
        project = Project()

        obj = CollectDataForIndicatorDashboard(project, None, None)
        self.assertEquals(obj.project, project)

    def test_that_indicator_type_is_set(self):
        indicator_type = 'Example Indicator type'
        obj = CollectDataForIndicatorDashboard(None, None, indicator_type)
        self.assertEquals(obj.indicator_type, indicator_type)

    def test_that_entity_is_null_when_entity_if_does_not_exist(self):
        entity_id = 42
        obj = CollectDataForIndicatorDashboard(None, entity_id, None)
        self.assertIsNone(obj.entity)

    def test_that_entity_is_fetched_from_db_the_given_entity_id_is_in_db(self):
        entity = EntityFactory.create()
        obj = CollectDataForIndicatorDashboard(None, entity.pk, None)
        self.assertEquals(obj.entity, entity)
