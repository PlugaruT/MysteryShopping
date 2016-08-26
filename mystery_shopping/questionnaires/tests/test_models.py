from django.test.testcases import TestCase
from mystery_shopping.factories.questionnaires import QuestionnaireTemplateFactory, QuestionnaireTemplateStatusFactory
from mystery_shopping.factories.users import UserFactory


class TestQuestionnaireTemplate(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.archived_questionnaire = QuestionnaireTemplateFactory(is_archived=True)
        self.unarchived_questionnaire = QuestionnaireTemplateFactory(is_archived=False)

    def test_archive_for_unarchived_questionnaire(self):
        self.unarchived_questionnaire.archive(self.user)
        self.assertTrue(self.unarchived_questionnaire.is_archived)

    def test_archive_for_archived_questionnaire(self):
        self.archived_questionnaire.archive(self.user)
        self.assertTrue(self.archived_questionnaire.is_archived)

    def test_unarchive_for_unarchived_questionnaire(self):
        self.unarchived_questionnaire.unarchive(self.user)
        self.assertFalse(self.unarchived_questionnaire.is_archived)

    def test_unarchive_for_archived_questionnaire(self):
        self.archived_questionnaire.unarchive(self.user)
        self.assertFalse(self.archived_questionnaire.is_archived)
