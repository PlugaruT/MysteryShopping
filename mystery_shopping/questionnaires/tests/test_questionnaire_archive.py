from rest_framework.reverse import reverse

from rest_framework.settings import api_settings
from rest_framework.test import APIClient, APITestCase

from mystery_shopping.factories.questionnaires import QuestionnaireTemplateFactory
from mystery_shopping.factories.users import TenantProductManagerFactory
from mystery_shopping.mystery_shopping_utils.jwt import jwt_response_payload_handler
from mystery_shopping.questionnaires.serializers import QuestionnaireTemplateSerializer
from mystery_shopping.users.models import User


class AuthenticateUser:
    def __init__(self):
        api_settings.JWT_RESPONSE_PAYLOAD_HANDLER = jwt_response_payload_handler
        self.credentials = {
            'username': 'consultant11',
            'password': 'moldova123'
        }
        self._set_user()
        self._attach_tennant_product_manager_to_user()
        self._set_client()

    def _set_user(self):
        self.user, _ = User.objects.get_or_create(username=self.credentials.get('username'))
        self.user.set_password(self.credentials.get('password'))
        self.user.save()

    def _attach_tennant_product_manager_to_user(self):
        TenantProductManagerFactory(user=self.user)

    def _set_client(self):
        self.client = APIClient(enforce_csrf_checks=True)
        response = self.client.post('/api-token-auth/', self.credentials, format='json')
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + response.data['token'])


class QuestionnaireTemplateArchiveAPITestCase(APITestCase):

    def setUp(self):
        self.archived_questionnaire = QuestionnaireTemplateFactory(is_archived=True)
        self.unarchived_questionnaire = QuestionnaireTemplateFactory(is_archived=False)

        self.user = AuthenticateUser().client

    def test_get_archived_questionnaires(self):
        response = self.user.get(reverse('questionnairetemplate-get-archived'))
        for questionnaire in response.data:
            self.assertTrue(questionnaire.get('is_archived'))

    def test_archive_questionnaire(self):
        self.user.put(reverse('questionnairetemplate-archive', args=(self.unarchived_questionnaire.id,)))
        self.unarchived_questionnaire.refresh_from_db()
        self.assertTrue(self.unarchived_questionnaire.is_archived)

    def test_unarchive_questionnaire(self):
        self.user.put(reverse('questionnairetemplate-unarchive', args=(self.archived_questionnaire.id,)))
        self.archived_questionnaire.refresh_from_db()
        self.assertFalse(self.archived_questionnaire.is_archived)

    def test_archive_archived_questionnaire(self):
        self.user.put(reverse('questionnairetemplate-archive', args=(self.archived_questionnaire.id,)))
        self.archived_questionnaire.refresh_from_db()
        self.assertTrue(self.archived_questionnaire.is_archived)

    def test_unarchive_unarchived_questionnaire(self):
        self.user.put(reverse('questionnairetemplate-unarchive', args=(self.unarchived_questionnaire.id,)))
        self.unarchived_questionnaire.refresh_from_db()
        self.assertFalse(self.unarchived_questionnaire.is_archived)
