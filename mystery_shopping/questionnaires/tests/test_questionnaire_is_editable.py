import json

from django.test.testcases import TestCase
from rest_framework import status
from rest_framework.reverse import reverse

from mystery_shopping.factories.questionnaires import QuestionnaireTemplateFactory, QuestionnaireTemplateBlockFactory, \
    QuestionTemplateFactory, QuestionnaireTemplateQuestionChoiceFactory
from mystery_shopping.users.tests.user_authentication import AuthenticateUser


class TestEditPermissionsOnQuestionnaires(TestCase):
    def setUp(self):
        self.authentication = AuthenticateUser()
        self.client = self.authentication.client
        self.questionnaire = QuestionnaireTemplateFactory(is_editable=False, tenant=self.authentication.tenant)
        self.block = QuestionnaireTemplateBlockFactory(questionnaire_template=self.questionnaire)
        self.question = QuestionTemplateFactory(questionnaire_template=self.questionnaire,
                                                             template_block=self.block)
        self.question_choice = QuestionnaireTemplateQuestionChoiceFactory(template_question=self.question)

    def test_edit_questionnaire_when_flag_is_false(self):
        response = self.client.put(reverse('questionnairetemplate-detail', args=(self.questionnaire.pk,)),
                                  data=json.dumps({'description': 'bababa',
                                                   'title': "demo title",
                                                   'tenant': self.authentication.tenant.id
                                                   }),
                                  content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_edit_questionnaire_when_flag_is_true(self):
        self.questionnaire.is_editable = True
        self.questionnaire.save()
        response = self.client.put(reverse('questionnairetemplate-detail', args=(self.questionnaire.pk,)),
                                  data=json.dumps({'description': 'bababa',
                                                   'title': "demo title",
                                                   'tenant': self.authentication.tenant.id
                                                   }),
                                  content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_edit_block_when_flag_is_false(self):

        response = self.client.put(reverse('questionnairetemplateblock-detail', args=(self.block.pk,)),
                                   data=json.dumps({'template_blocks': [{
                                       'title': 'modified title',
                                       'weight': 3,
                                       'order': 1,
                                       'template_questions': [{
                                           'id': 1,
                                           "question_body": "Iluminarea fațadei",
                                           "order": 1,
                                           "weight": "40.00",
                                       }]
                                   }],
                                       'description': 'some another',
                                       'title': "demo title",
                                       'tenant': self.authentication.tenant.id
                                   }),
                                   content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_edit_block_when_flag_is_true(self):
        self.questionnaire.is_editable = True
        self.questionnaire.save()
        response = self.client.put(reverse('questionnairetemplateblock-detail', args=(self.block.pk,)),
                                   data=json.dumps({'template_blocks': [{
                                       'title': 'modified title',
                                       'id': 11,
                                       'weight': 3,
                                       'order': 11,
                                       'template_questions': [{
                                           'id': 1,
                                           "question_body": "Iluminarea fațadei",
                                           "order": 1,
                                           "weight": "22.0",
                                       }]
                                   }],
                                       "weight": "5.00",
                                       "order": 1,
                                       'description': 'some descr',
                                       'title': "demo title aaaa",
                                       'tenant': self.authentication.tenant.id,
                                       'template_questions': [{
                                           'id': 1,
                                           "question_body": "Iluminarea fațadei",
                                           "order": 1,
                                           "weight": "22.0",
                                       }]
                                   }),
                                   content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_edit_question_when_flag_is_false(self):
        response = self.client.put(reverse('questionnairetemplatequestion-detail', args=(self.question.pk,)),
                                   data=json.dumps({
                                       'tenant': self.authentication.tenant.id,
                                       "question_body": "qqweqw?",
                                       "max_score": 15,
                                       "order": 1,
                                       "weight": "44.64",
                                   }),
                                   content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_edit_question_when_flag_is_true(self):
        self.questionnaire.is_editable = True
        self.questionnaire.save()
        response = self.client.put(reverse('questionnairetemplatequestion-detail', args=(self.question.pk,)),
                                   data=json.dumps({
                                       'tenant': self.authentication.tenant.id,
                                       "question_body": "qqweqw?",
                                       "max_score": 15,
                                       "order": 1,
                                       "weight": "44.64",
                                   }),
                                   content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_edit_question_choice_when_flag_is_false(self):
        response = self.client.put(reverse('questionnairetemplatequestionchoice-detail', args=(self.question_choice.pk,)),
                                   data=json.dumps({
                                       "question_body": "wassap?",
                                       'order': 1,
                                       'tenant': self.authentication.tenant.id,
                                   }),
                                   content_type='application/json')

        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_edit_question_choice_when_flag_is_true(self):
        self.questionnaire.is_editable = True
        self.questionnaire.save()
        response = self.client.put(reverse('questionnairetemplatequestionchoice-detail', args=(self.question_choice.pk,)),
                                   data=json.dumps({
                                       "question_body": "wassap?",
                                       'order': 1,
                                       'tenant': self.authentication.tenant.id,
                                   }),
                                   content_type='application/json')

        self.assertEquals(response.status_code, status.HTTP_200_OK)
