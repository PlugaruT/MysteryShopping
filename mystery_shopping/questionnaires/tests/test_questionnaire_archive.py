from rest_framework.reverse import reverse

from rest_framework.test import APITestCase

from mystery_shopping.factories.questionnaires import QuestionnaireTemplateFactory, QuestionnaireTemplateStatusFactory
from mystery_shopping.factories.users import UserFactory
from mystery_shopping.users.tests.user_authentication import AuthenticateUser


class QuestionnaireTemplateArchiveAPITestCase(APITestCase):

    def setUp(self):
        self.archived_questionnaire = QuestionnaireTemplateFactory(is_archived=True)
        self.unarchived_questionnaire = QuestionnaireTemplateFactory(is_archived=False)

        self.authentification = AuthenticateUser()
        self.client = self.authentification.client

    def test_get_archived_questionnaires(self):
        response = self.client.get(reverse('questionnairetemplate-get-archived'))
        for questionnaire in response.data:
            self.assertTrue(questionnaire.get('is_archived'))

    def test_get_unarchived_questionnaires(self):
        response = self.client.get(reverse('questionnairetemplate-get-unarchived'))
        for questionnaire in response.data:
            self.assertFalse(questionnaire.get('is_archived'))

    def test_archive_unarchived_questionnaire(self):
        self.client.put(reverse('questionnairetemplate-archive', args=(self.unarchived_questionnaire.id,)))
        self.unarchived_questionnaire.refresh_from_db()
        self.assertTrue(self.unarchived_questionnaire.is_archived)

    def test_unarchive_archived_questionnaire(self):
        self.client.put(reverse('questionnairetemplate-unarchive', args=(self.archived_questionnaire.id,)))
        self.archived_questionnaire.refresh_from_db()
        self.assertFalse(self.archived_questionnaire.is_archived)

    def test_archive_archived_questionnaire(self):
        self.client.put(reverse('questionnairetemplate-archive', args=(self.archived_questionnaire.id,)))
        self.archived_questionnaire.refresh_from_db()
        self.assertTrue(self.archived_questionnaire.is_archived)

    def test_unarchive_unarchived_questionnaire(self):
        self.client.put(reverse('questionnairetemplate-unarchive', args=(self.unarchived_questionnaire.id,)))
        self.unarchived_questionnaire.refresh_from_db()
        self.assertFalse(self.unarchived_questionnaire.is_archived)
