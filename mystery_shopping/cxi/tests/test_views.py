from django.http.request import QueryDict
from rest_framework import status
from rest_framework.reverse import reverse

from rest_framework.test import APITestCase

from mystery_shopping.factories.cxi import CodedCauseFactory
from mystery_shopping.users.tests.user_authentication import AuthenticateUser


class CodedCausesAPITestCase(APITestCase):
    def setUp(self):
        self.authentication = AuthenticateUser()
        self.client = self.authentication.client
        user = self.authentication.user
        self.coded_cause = CodedCauseFactory(tenant=user.tenant)

    def test_create_coded_cause_with_responsible_user(self):
        pass
