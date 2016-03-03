import json

from django.test import TestCase

from rest_assured.testcases import ReadWriteRESTAPITestCaseMixin, BaseRESTAPITestCase

from mystery_shopping.factories.questionnaires import QuestionnaireTemplateFactory
from mystery_shopping.factories.questionnaires import QuestionnaireTemplateBlockDefaultFactory
from mystery_shopping.factories.questionnaires import QuestionnaireTemplateBlockFactory
from mystery_shopping.factories.users import UserThatIsTenantProductManagerFactory


class QuestionnaireTemplateBlockAPITestCase(ReadWriteRESTAPITestCaseMixin, BaseRESTAPITestCase):

    base_name = 'questionnairetemplateblock'
    factory_class = QuestionnaireTemplateBlockFactory
    user_factory = UserThatIsTenantProductManagerFactory

    def test_create(self, data=None, **kwargs):
        kwargs['format'] = 'json'
        super(QuestionnaireTemplateBlockAPITestCase, self).test_create(data, **kwargs)

    def get_create_data(self):
        sibling_block = QuestionnaireTemplateBlockDefaultFactory(
            questionnaire_template=self.object.questionnaire_template)
        self.data = json.loads('''{
                               "template_questions":[],
                               "title":"Test Template Block",
                               "weight":"5.00",
                               "parent_block": null
                                }''')
        self.data['siblings'] = [{'block_id': sibling_block.id, 'block_changes': {'weight': 2.9}}]
        self.data['questionnaire_template'] = self.object.questionnaire_template.id
        self.data['order'] = self.object.order
        return self.data

    def get_update_data(self):
        self.data = {'title': 'Updated Title',
                     'order': 10}
        # import pdb; pdb.run('')
        return self.data


