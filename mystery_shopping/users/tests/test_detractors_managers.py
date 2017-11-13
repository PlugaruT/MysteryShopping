from unittest import TestCase

from mystery_shopping.factories.projects import ProjectFactory
from mystery_shopping.factories.users import ClientUserFactory
from mystery_shopping.users.serializers import ClientUserSerializerGET


class TestDetractorsManagersForProject(TestCase):
    def setUp(self):
        self.client_user = ClientUserFactory()
        self.project = ProjectFactory(detractors_manager=self.client_user.user)

    def test_serialize_detractor_manager_with_projects(self):
        actual_data = ClientUserSerializerGET(self.client_user).data

        self.assertEqual(actual_data.get('detractor_manager_to_projects'), [self.project.pk])

    def test_serialize_detractor_managers_without_projects(self):
        self.project.detractors_manager = None
        self.project.save()

        actual_data = ClientUserSerializerGET(self.client_user).data

        self.assertIsNone(actual_data.get('detractors_manager_to_projects'))
