import json
from decimal import Decimal

from rest_framework.reverse import reverse
from rest_framework.settings import api_settings
from rest_framework.test import APIRequestFactory, APIClient, APITestCase

from rest_assured.testcases import CreateAPITestCaseMixin
from rest_assured.testcases import ReadWriteRESTAPITestCaseMixin
from rest_assured.testcases import BaseRESTAPITestCase

from mystery_shopping.mystery_shopping_utils.jwt import jwt_response_payload_handler
from mystery_shopping.questionnaires.serializers import QuestionnaireTemplateSerializer
from mystery_shopping.users.models import User
from ..models import QuestionnaireTemplateBlock
from ..models import QuestionnaireTemplateQuestion
from ..serializers import QuestionnaireTemplateBlockSerializer
from ..serializers import QuestionnaireTemplateQuestionSerializer
from mystery_shopping.factories.questionnaires import QuestionnaireTemplateFactory
from mystery_shopping.factories.questionnaires import QuestionnaireTemplateBlockFactory
from mystery_shopping.factories.questionnaires import QuestionnaireTemplateQuestionFactory
from mystery_shopping.factories.users import UserThatIsTenantProductManagerFactory, TenantProductManagerFactory
from mystery_shopping.factories.tenants import TenantFactory


class QuestionnaireTemplateAPITestCase(CreateAPITestCaseMixin, BaseRESTAPITestCase):
    base_name = 'questionnairetemplate'
    factory_class = QuestionnaireTemplateFactory
    user_factory = UserThatIsTenantProductManagerFactory

    def setUp(self):
        self.json_data = json.load(open("mystery_shopping/questionnaires/tests/QuestionnaireTemplates.json"))
        super(QuestionnaireTemplateAPITestCase, self).setUp()

    def get_create_data(self):
        tenant = TenantFactory()
        self.data = self.json_data[1]
        self.data['tenant'] = tenant.id
        return self.data


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
        self.questionnaire1 = QuestionnaireTemplateFactory(is_archived=True)
        self.questionnaire2 = QuestionnaireTemplateFactory(is_archived=False)
        self.serializer = QuestionnaireTemplateSerializer(self.questionnaire1)
        self.factory = APIRequestFactory()

        self.user = AuthenticateUser().client

    def test_get_archived_questionnaires(self):
        response = self.user.get(reverse('questionnairetemplate-get-archived'))
        for questionnaire in response.data:
            self.assertTrue(questionnaire.get('is_archived'))

    def test_archive_questionnaire(self):
        self.user.post(reverse('questionnairetemplate-archive', args=(self.questionnaire2.id,)))
        self.questionnaire2.refresh_from_db()
        self.assertTrue(self.questionnaire2.is_archived)

    def test_unarchive_questionnaire(self):
        self.user.post(reverse('questionnairetemplate-unarchive', args=(self.questionnaire1.id,)))
        self.questionnaire1.refresh_from_db()
        self.assertFalse(self.questionnaire1.is_archived)

    def test_when_archive_and_then_unarchive_questionnaire(self):
        self.user.post(reverse('questionnairetemplate-archive', args=(self.questionnaire2.id,)))
        self.questionnaire2.refresh_from_db()
        self.user.post(reverse('questionnairetemplate-unarchive', args=(self.questionnaire2.id,)))
        self.questionnaire2.refresh_from_db()
        self.assertFalse(self.questionnaire2.is_archived)


class QuestionnaireTemplateBlockAPITestCase(ReadWriteRESTAPITestCaseMixin, BaseRESTAPITestCase):

    base_name = 'questionnairetemplateblock'
    factory_class = QuestionnaireTemplateBlockFactory
    user_factory = UserThatIsTenantProductManagerFactory

    def setUp(self):
        self.json_data = json.load(open("mystery_shopping/questionnaires/tests/QuestionnaireTemplateBlocks.json"))
        super(QuestionnaireTemplateBlockAPITestCase, self).setUp()

    def get_create_data(self):
        sibling_block = QuestionnaireTemplateBlockFactory(
            questionnaire_template=self.object.questionnaire_template)

        self.data = self.json_data[1]
        self.data['siblings'] = [{'block_id': sibling_block.id, 'block_changes': {'weight': 2.9}}]
        self.data['questionnaire_template'] = self.object.questionnaire_template.id
        self.data['order'] = self.object.order
        return self.data

    def get_update_data(self):
        self.data = {'title': 'Updated Title',
                     'order': 10,
                     'questionnaire_template': str(self.object.questionnaire_template.id)}
        return self.data

    def test_create(self, data=None, **kwargs):
        kwargs['format'] = 'json'
        super(QuestionnaireTemplateBlockAPITestCase, self).test_create(data, **kwargs)

    def test_update_with_sibling(self):
        sibling_new_weight = 2.9
        sibling_new_order = 2

        # Create the first block
        sibling_block = QuestionnaireTemplateBlockFactory(
            questionnaire_template=self.object.questionnaire_template, order=1)

        # Create another block that should update the first one
        self.data = self.json_data[0]
        self.data['siblings'] = [{'block_id': sibling_block.id,
                                  'block_changes': {'weight': sibling_new_weight, 'order': sibling_new_order}}]
        self.data['questionnaire_template'] = self.object.questionnaire_template.id
        self.data['order'] = self.object.order
        new_block = QuestionnaireTemplateBlockSerializer(data=self.data)
        new_block.is_valid()
        new_block.save()

        sibling_block = QuestionnaireTemplateBlock.objects.get(pk=sibling_block.pk)

        self.assertEqual(sibling_block.order, sibling_new_order)
        self.assertEqual(sibling_block.weight, round(Decimal(sibling_new_weight), 2))

    def test_recalculate_sibling_order(self):
        initial_orders = [1, 2, 3]
        siblings = []
        for i in initial_orders:
            siblings.append(QuestionnaireTemplateBlockFactory(
                questionnaire_template=self.object.questionnaire_template, order=i,
                title='Template Block {}'.format(i)))

        # Delete one block
        to_delete = siblings.pop(0)
        self.client.delete(reverse('{}-detail'.format(self.base_name), kwargs={'pk': to_delete.pk}))

        for i, sibling in enumerate(siblings):
            sibling = QuestionnaireTemplateBlock.objects.get(pk=sibling.pk)
            # Assert whether the order has been recalculated
            self.assertEqual(sibling.order, i + 1)


class QuestionnaireTemplateQuestionAPITestCase(ReadWriteRESTAPITestCaseMixin, BaseRESTAPITestCase):

    base_name = 'questionnairetemplatequestion'
    factory_class = QuestionnaireTemplateQuestionFactory
    user_factory = UserThatIsTenantProductManagerFactory

    def setUp(self):
        self.json_data = json.load(open("mystery_shopping/questionnaires/tests/QuestionnaireTemplateQuestions.json"))
        super(QuestionnaireTemplateQuestionAPITestCase, self).setUp()

    def get_create_data(self):
        self.data = self.json_data[0]
        self.data['questionnaire_template'] = self.object.questionnaire_template.id
        self.data['template_block'] = self.object.template_block.id
        return self.data

    def get_update_data(self):
        self.data = {'question_body': 'Updated Body',
                     'order': 10}
        return self.data

    def test_create(self, data=None, **kwargs):
        kwargs['format'] = 'json'
        super(QuestionnaireTemplateQuestionAPITestCase, self).test_create(data, **kwargs)

    def test_update_with_sibling(self):
        sibling_new_weight = 2.9
        sibling_new_order = 2

        # Create the first question
        sibling_question = QuestionnaireTemplateQuestionFactory(
            questionnaire_template=self.object.questionnaire_template, template_block=self.object.template_block, order=1)

        # Create another question that should update the first one
        self.data = self.json_data[1]
        self.data['siblings'] = [{'question_id': sibling_question.id,
                                  'question_changes': {'weight': sibling_new_weight, 'order': sibling_new_order}}]
        self.data['questionnaire_template'] = self.object.questionnaire_template.id
        self.data['template_block'] = self.object.template_block.id
        new_block = QuestionnaireTemplateQuestionSerializer(data=self.data)
        new_block.is_valid()
        new_block.save()

        sibling_question = QuestionnaireTemplateQuestion.objects.get(pk=sibling_question.pk)

        self.assertEqual(sibling_question.order, sibling_new_order)
        self.assertEqual(sibling_question.weight, round(Decimal(sibling_new_weight), 2))

    def test_recalculate_sibling_order(self):
        initial_orders = [1, 2, 3, 4]
        siblings = []
        for i in initial_orders:
            siblings.append(QuestionnaireTemplateQuestionFactory(
                questionnaire_template=self.object.questionnaire_template,
                template_block=self.object.template_block, order=i,
                question_body='Template Question {}'.format(i)))

        # Delete one question
        to_delete = siblings.pop(2)
        self.client.delete(reverse('{}-detail'.format(self.base_name), kwargs={'pk': to_delete.pk}))

        for i, sibling in enumerate(siblings):
            sibling = QuestionnaireTemplateQuestion.objects.get(pk=sibling.pk)
            # Assert whether the order has been recalculated
            self.assertEqual(sibling.order, i + 1)
