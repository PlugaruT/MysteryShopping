from django.contrib.auth.models import Group
from rest_framework.settings import api_settings
from rest_framework.test import APIClient

from mystery_shopping.factories.users import TenantProductManagerFactory
from mystery_shopping.mystery_shopping_utils.jwt import jwt_response_payload_handler
from mystery_shopping.tenants.models import Tenant
from mystery_shopping.users.models import User
from mystery_shopping.users.roles import UserRole


class AuthenticateUser:
    def __init__(self, tenant=None):
        api_settings.JWT_RESPONSE_PAYLOAD_HANDLER = jwt_response_payload_handler
        self.credentials = {
            'username': 'user_test',
            'password': 'moldova123'
        }
        if tenant is None:
            self.tenant = Tenant.objects.create(name='tenant demo')
        else:
            self.tenant = tenant
        self._set_user()
        # self._attach_tenant_product_manager_to_user()
        self._set_client()

    def _set_user(self):
        self.user, _ = User.objects.get_or_create(username=self.credentials.get('username'), tenant=self.tenant)
        self.user.set_password(self.credentials.get('password'))
        self.user.save()
        group, _ = Group.objects.get_or_create(name=UserRole.TENANT_PRODUCT_MANAGER_GROUP)
        group.user_set.add(self.user)

    def _attach_tenant_product_manager_to_user(self):
        TenantProductManagerFactory(user=self.user, tenant=self.tenant)

    def _set_client(self):
        self.client = APIClient(enforce_csrf_checks=True)
        response = self.client.post('/api-token-auth/', self.credentials, format='json')
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + response.data['token'])
