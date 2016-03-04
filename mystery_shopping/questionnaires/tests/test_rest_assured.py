import json
from decimal import Decimal

from rest_framework.reverse import reverse

from rest_assured.testcases import ReadWriteRESTAPITestCaseMixin
from rest_assured.testcases import BaseRESTAPITestCase

from ..models import QuestionnaireTemplateBlock
from ..serializers import QuestionnaireTemplateBlockSerializer
from mystery_shopping.factories.questionnaires import QuestionnaireTemplateBlockFactory
from mystery_shopping.factories.questionnaires import QuestionnaireTemplateQuestionFactory
from mystery_shopping.factories.users import UserThatIsTenantProductManagerFactory


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
