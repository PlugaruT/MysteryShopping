from rest_framework.settings import api_settings
from rest_framework.test import APIClient

from mystery_shopping.factories.users import TenantProductManagerFactory
from mystery_shopping.mystery_shopping_utils.jwt import jwt_response_payload_handler
from mystery_shopping.tenants.models import Tenant
from mystery_shopping.users.models import User


class AuthenticateUser:
    def __init__(self):
        api_settings.JWT_RESPONSE_PAYLOAD_HANDLER = jwt_response_payload_handler
        self.credentials = {
            'username': 'admin',
            'password': 'moldova123'
        }
        self.tenant = Tenant.objects.create(name='tenant demo')
        self._set_user()
        self._attach_tennant_product_manager_to_user()
        self._set_client()

    def _set_user(self):
        self.user, _ = User.objects.get_or_create(username=self.credentials.get('username'))
        self.user.set_password(self.credentials.get('password'))
        self.user.save()

    def _attach_tennant_product_manager_to_user(self):
        TenantProductManagerFactory(user=self.user, tenant=self.tenant)

    def _set_client(self):
        self.client = APIClient(enforce_csrf_checks=True)
        response = self.client.post('/api-token-auth/', self.credentials, format='json')
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + response.data['token'])
