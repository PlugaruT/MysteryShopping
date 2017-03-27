from django.test.testcases import TestCase
from rest_framework.reverse import reverse

from mystery_shopping.factories.questionnaires import QuestionnaireTemplateFactory, QuestionnaireTemplateBlockFactory, \
    QuestionTemplateFactory
from mystery_shopping.users.tests.user_authentication import AuthenticateUser


class TestTemplateQuestionSpecialFlags(TestCase):
    def setUp(self):
        self.authentication = AuthenticateUser()
        self.client = self.authentication.client
        self.questionnaire = QuestionnaireTemplateFactory(is_editable=False, tenant=self.authentication.tenant)
        self.block = QuestionnaireTemplateBlockFactory(questionnaire_template=self.questionnaire)
        self.question = QuestionTemplateFactory(questionnaire_template=self.questionnaire,
                                                template_block=self.block)

    def test_deny_why_causes_from_true(self):
        self.question.allow_why_causes = True
        self.question.save()
        self.client.put(reverse('questionnairetemplatequestion-deny-why-causes', args=(self.question.pk,)))

        self.question.refresh_from_db()
        self.assertFalse(self.question.allow_why_causes)

    def test_deny_why_causes_from_false(self):
        self.question.allow_why_causes = False
        self.question.save()
        self.client.put(reverse('questionnairetemplatequestion-deny-why-causes', args=(self.question.pk,)))

        self.question.refresh_from_db()
        self.assertFalse(self.question.allow_why_causes)

    def test_allow_why_causes_from_true(self):
        self.question.allow_why_causes = True
        self.question.save()
        self.client.put(reverse('questionnairetemplatequestion-allow-why-causes', args=(self.question.pk,)))

        self.question.refresh_from_db()
        self.assertTrue(self.question.allow_why_causes)

    def test_allow_why_causes_from_false(self):
        self.question.allow_why_causes = False
        self.question.save()
        self.client.put(reverse('questionnairetemplatequestion-allow-why-causes', args=(self.question.pk,)))

        self.question.refresh_from_db()
        self.assertTrue(self.question.allow_why_causes)

    def test_deny_other_choices_from_true(self):
        self.question.has_other_choice = True
        self.question.save()
        self.client.put(reverse('questionnairetemplatequestion-deny-other-choices', args=(self.question.pk,)))

        self.question.refresh_from_db()
        self.assertFalse(self.question.has_other_choice)

    def test_deny_other_choices_from_false(self):
        self.question.has_other_choice = False
        self.question.save()
        self.client.put(reverse('questionnairetemplatequestion-deny-other-choices', args=(self.question.pk,)))

        self.question.refresh_from_db()
        self.assertFalse(self.question.has_other_choice)

    def test_allow_other_choices_from_true(self):
        self.question.has_other_choice = True
        self.question.save()
        self.client.put(reverse('questionnairetemplatequestion-allow-other-choices', args=(self.question.pk,)))

        self.question.refresh_from_db()
        self.assertTrue(self.question.has_other_choice)

    def test_allow_other_choices_from_false(self):
        self.question.has_other_choice = False
        self.question.save()
        self.client.put(reverse('questionnairetemplatequestion-allow-other-choices', args=(self.question.pk,)))

        self.question.refresh_from_db()
        self.assertTrue(self.question.has_other_choice)

    def test_unset_new_algorithm_from_true(self):
        self.question.new_algorithm = True
        self.question.save()
        self.client.put(reverse('questionnairetemplatequestion-unset-new-algorithm', args=(self.question.pk,)))

        self.question.refresh_from_db()
        self.assertFalse(self.question.new_algorithm)

    def test_unset_new_algorithm_from_false(self):
        self.question.new_algorithm = False
        self.question.save()
        self.client.put(reverse('questionnairetemplatequestion-unset-new-algorithm', args=(self.question.pk,)))

        self.question.refresh_from_db()
        self.assertFalse(self.question.new_algorithm)

    def test_set_new_algorithmfrom_true(self):
        self.question.new_algorithm = True
        self.question.save()
        self.client.put(reverse('questionnairetemplatequestion-set-new-algorithm', args=(self.question.pk,)))

        self.question.refresh_from_db()
        self.assertTrue(self.question.new_algorithm)

    def test_set_new_algorithmfrom_false(self):
        self.question.new_algorithm = False
        self.question.save()
        self.client.put(reverse('questionnairetemplatequestion-set-new-algorithm', args=(self.question.pk,)))

        self.question.refresh_from_db()
        self.assertTrue(self.question.new_algorithm)
