from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from mystery_shopping.factories.tenants import TenantFactory
from mystery_shopping.factories.users import UserFactory, ShopperFactory, ClientUserFactory
from mystery_shopping.users.models import Shopper, User
from mystery_shopping.users.tests.user_authentication import AuthenticateUser


class ShopperAPITestCase(APITestCase):
    def setUp(self):
        self.tenant = TenantFactory()
        self.authentication = AuthenticateUser(tenant=self.tenant)
        self.client = self.authentication.client
        self.user = UserFactory(tenant=self.tenant)
        self.shopper = ShopperFactory(user=self.user)

    def test_destroy(self):
        response = self.client.delete(reverse('shopper-detail', args=(self.shopper.id,)))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, response.data)
        self.assertRaises(ObjectDoesNotExist, Shopper.objects.get, id=self.shopper.id)
        self.assertRaises(ObjectDoesNotExist, User.objects.get, id=self.user.id)


class ClientUserAPITestCase(APITestCase):
    def setUp(self):
        self.tenant = TenantFactory()
        self.authentication = AuthenticateUser(tenant=self.tenant)
        self.client = self.authentication.client
        self.user = UserFactory(tenant=self.tenant)
        self.client_user = ClientUserFactory(user=self.user)

    def test_destroy(self):
        response = self.client.delete(reverse('clientuser-detail', args=(self.client_user.id,)))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, response.data)
        self.assertRaises(ObjectDoesNotExist, Shopper.objects.get, id=self.client_user.id)
        self.assertRaises(ObjectDoesNotExist, User.objects.get, id=self.user.id)
