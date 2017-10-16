from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from mystery_shopping.cxi.models import CodedCause, CodedCauseLabel
from mystery_shopping.factories.projects import ProjectFactory
from mystery_shopping.factories.users import ClientUserFactory
from mystery_shopping.users.serializers import ClientUserSerializer
from mystery_shopping.users.tests.user_authentication import AuthenticateUser


class CodedCausesAPITestCase(APITestCase):
    def setUp(self):
        self.authentication = AuthenticateUser()
        self.client = self.authentication.client
        self.user = self.authentication.user
        self.project = ProjectFactory(tenant=self.user.tenant)

        self.coded_cause_label = 'random_name'
        self.data = {
            'coded_label': {
                'name': self.coded_cause_label,
            },
            'project': self.project.id,
            'sentiment': 'a',
            'type': 'indicator',
            'parent': None
        }

    def test_create_coded_cause_without_responsible_users(self):
        response = self.client.post(reverse('codedcause-list'), data=self.data, format='json')

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertCodedCauseCreation()

    def test_create_coded_cause_with_responsible_users(self):
        user = self._create_client_user()
        self.data['responsible_users'] = [user.id]
        print(self.data)
        response = self.client.post(reverse('codedcause-list'), data=self.data, format='json')
        print(response.data)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertCodedCauseCreation()

    def test_if_users_are_set_on_coded_cause_creation_with_responsible_users(self):
        user = self._create_client_user()
        self.data['responsible_users'] = [user.id]
        print(self.data)
        self.client.post(reverse('codedcause-list'), data=self.data, format='json')

        coded_cause_instance = CodedCause.objects.get(coded_label__name=self.coded_cause_label)
        coded_cause_responsible_users = list(coded_cause_instance.responsible_users.all())

        self.assertListEqual([user], coded_cause_responsible_users)

    def test_if_users_are_set_on_coded_cause_creation_without_responsible_users(self):
        self.client.post(reverse('codedcause-list'), data=self.data, format='json')

        coded_cause_instance = CodedCause.objects.get(coded_label__name=self.coded_cause_label)
        coded_cause_responsible_users = list(coded_cause_instance.responsible_users.all())

        self.assertListEqual([], coded_cause_responsible_users)

    def assertCodedCauseCreation(self):
        self.assertEqual(1, CodedCause.objects.count())
        self.assertEqual(1, CodedCauseLabel.objects.count())

    @staticmethod
    def _create_client_user():
        user_1 = ClientUserFactory()
        serialized_user = ClientUserSerializer(user_1)
        return serialized_user.instance
