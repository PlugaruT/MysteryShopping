from django.test.testcases import TestCase
from mystery_shopping.factories.questionnaires import QuestionnaireTemplateFactory


class TestQuestionnaireTemplate(TestCase):
    def setUp(self):
        self.archived_questionnaire = QuestionnaireTemplateFactory(is_archived=True)
        self.unarchived_questionnaire = QuestionnaireTemplateFactory(is_archived=False)

    def test_archive_for_unarchived_questionnaire(self):
        self.unarchived_questionnaire.archive()
        self.assertTrue(self.unarchived_questionnaire)

    def test_archive_for_archived_questionnaire(self):
        self.archived_questionnaire.archive()
        self.assertTrue(self.archived_questionnaire)

    def test_unarchive_for_unarchived_questionnaire(self):
        self.unarchived_questionnaire.unarchive()
        self.assertFalse(self.unarchived_questionnaire.is_archived)

    def test_unarchive_for_archived_questionnaire(self):
        self.archived_questionnaire.unarchive()
        self.assertFalse(self.archived_questionnaire.is_archived)
