import json

from rest_assured.testcases import ReadWriteRESTAPITestCaseMixin, BaseRESTAPITestCase

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
        self.data = json.loads('''{
                               "template_questions":[],
                               "title":"Test Template Block",
                               "weight":"5.00",
                               "parent_block": null
                                }''')
        self.data['questionnaire_template'] = self.object.questionnaire_template.id
        self.data['order'] = self.object.order
        return self.data

    def get_update_data(self):
        self.data = {'title': 'Updated Title',
                     'order': 10}
        return self.data
