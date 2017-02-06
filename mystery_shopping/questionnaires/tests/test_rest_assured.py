import json
from decimal import Decimal

from rest_framework.reverse import reverse

from rest_assured.testcases import CreateAPITestCaseMixin
from rest_assured.testcases import ReadWriteRESTAPITestCaseMixin
from rest_assured.testcases import BaseRESTAPITestCase

from ..models import QuestionnaireTemplateBlock
from ..models import QuestionnaireTemplateQuestion
from ..serializers import QuestionnaireTemplateBlockSerializer
from ..serializers import QuestionnaireTemplateQuestionSerializer
from mystery_shopping.factories.questionnaires import QuestionnaireTemplateFactory, QuestionnaireTemplateStatusFactory
from mystery_shopping.factories.questionnaires import QuestionnaireTemplateBlockFactory
from mystery_shopping.factories.questionnaires import QuestionTemplateFactory
from mystery_shopping.factories.users import UserThatIsTenantProductManagerFactory, UserFactory, \
    TenantProductManagerGroupFactory
from mystery_shopping.factories.tenants import TenantFactory


class QuestionnaireTemplateAPITestCase(CreateAPITestCaseMixin, BaseRESTAPITestCase):
    base_name = 'questionnairetemplate'
    factory_class = QuestionnaireTemplateFactory
    user_factory = UserThatIsTenantProductManagerFactory

    def setUp(self):
        with open("mystery_shopping/questionnaires/tests/QuestionnaireTemplates.json") as file:
            self.json_data = json.load(file)
        super(QuestionnaireTemplateAPITestCase, self).setUp()

    def test_create(self, data=None, **kwargs):
        group = TenantProductManagerGroupFactory.create()
        self.user.groups.add(group)
        super(QuestionnaireTemplateAPITestCase, self).test_create(data, **kwargs)

    def get_create_data(self):
        tenant = TenantFactory()
        status = QuestionnaireTemplateStatusFactory()
        created_by = UserFactory()
        self.data = self.json_data[1]
        self.data['tenant'] = tenant.id
        self.data['status'] = status.id
        self.data['created_by'] = created_by.id
        return self.data


class QuestionnaireTemplateBlockAPITestCase(ReadWriteRESTAPITestCaseMixin, BaseRESTAPITestCase):
    base_name = 'questionnairetemplateblock'
    factory_class = QuestionnaireTemplateBlockFactory
    user_factory = UserThatIsTenantProductManagerFactory

    def setUp(self):
        with open("mystery_shopping/questionnaires/tests/QuestionnaireTemplateBlocks.json") as file:
            self.json_data = json.load(file)
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
        group = TenantProductManagerGroupFactory.create()
        self.user.groups.add(group)
        super(QuestionnaireTemplateBlockAPITestCase, self).test_create(data, **kwargs)

    def test_destroy(self, **kwargs):
        group = TenantProductManagerGroupFactory.create()
        self.user.groups.add(group)
        super(QuestionnaireTemplateBlockAPITestCase, self).test_destroy(**kwargs)

    def test_list(self, **kwargs):
        group = TenantProductManagerGroupFactory.create()
        self.user.groups.add(group)
        super(QuestionnaireTemplateBlockAPITestCase, self).test_list(**kwargs)

    def test_update(self, data=None, results=None, use_patch=None, **kwargs):
        group = TenantProductManagerGroupFactory.create()
        self.user.groups.add(group)
        super(QuestionnaireTemplateBlockAPITestCase, self).test_update(**kwargs)

    def test_detail(self, **kwargs):
        group = TenantProductManagerGroupFactory.create()
        self.user.groups.add(group)
        super(QuestionnaireTemplateBlockAPITestCase, self).test_detail(**kwargs)

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

    def _test_recalculate_sibling_order(self):
        initial_orders = [1, 2, 3]
        siblings = []
        for order in initial_orders:
            siblings.append(QuestionnaireTemplateBlockFactory(
                questionnaire_template=self.object.questionnaire_template, order=order,
                title='Template Block {}'.format(order)))

        # Delete one block
        to_delete = siblings.pop(0)
        self.client.delete(reverse('{}-detail'.format(self.base_name), kwargs={'pk': to_delete.pk}))
        for order, sibling in enumerate(siblings):
            sibling = QuestionnaireTemplateBlock.objects.get(pk=sibling.pk)
            # Assert whether the order has been recalculated
            self.assertEqual(sibling.order, order + 1)


class QuestionnaireTemplateQuestionAPITestCase(ReadWriteRESTAPITestCaseMixin, BaseRESTAPITestCase):
    base_name = 'questionnairetemplatequestion'
    factory_class = QuestionTemplateFactory
    user_factory = UserThatIsTenantProductManagerFactory

    def setUp(self):
        with open("mystery_shopping/questionnaires/tests/QuestionnaireTemplateQuestions.json") as file:
            self.json_data = json.load(file)
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
        group = TenantProductManagerGroupFactory.create()
        self.user.groups.add(group)
        super(QuestionnaireTemplateQuestionAPITestCase, self).test_create(data, **kwargs)

    def test_destroy(self, **kwargs):
        group = TenantProductManagerGroupFactory.create()
        self.user.groups.add(group)
        super(QuestionnaireTemplateQuestionAPITestCase, self).test_destroy(**kwargs)

    def test_list(self, **kwargs):
        group = TenantProductManagerGroupFactory.create()
        self.user.groups.add(group)
        super(QuestionnaireTemplateQuestionAPITestCase, self).test_list(**kwargs)

    def test_update(self, data=None, results=None, use_patch=None, **kwargs):
        group = TenantProductManagerGroupFactory.create()
        self.user.groups.add(group)
        super(QuestionnaireTemplateQuestionAPITestCase, self).test_update(**kwargs)

    def test_detail(self, **kwargs):
        group = TenantProductManagerGroupFactory.create()
        self.user.groups.add(group)
        super(QuestionnaireTemplateQuestionAPITestCase, self).test_detail(**kwargs)

    def test_update_with_sibling(self):
        sibling_new_weight = 2.9
        sibling_new_order = 2

        # Create the first question
        sibling_question = QuestionTemplateFactory(
            questionnaire_template=self.object.questionnaire_template, template_block=self.object.template_block,
            order=1)

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

    def _test_recalculate_sibling_order(self):
        initial_orders = [1, 2, 3, 4]
        siblings = []
        for order in initial_orders:
            siblings.append(QuestionTemplateFactory(
                questionnaire_template=self.object.questionnaire_template,
                template_block=self.object.template_block, order=order,
                question_body='Template Question {}'.format(order)))

        # Delete one question
        to_delete = siblings.pop(2)
        self.client.delete(reverse('{}-detail'.format(self.base_name), kwargs={'pk': to_delete.pk}))

        for order, sibling in enumerate(siblings):
            sibling = QuestionnaireTemplateQuestion.objects.get(pk=sibling.pk)
            # Assert whether the order has been recalculated
            self.assertEqual(sibling.order, order + 1)
