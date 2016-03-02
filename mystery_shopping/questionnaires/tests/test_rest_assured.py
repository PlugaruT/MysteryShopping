import json

from rest_assured.testcases import ReadWriteRESTAPITestCaseMixin, BaseRESTAPITestCase

from mystery_shopping.factories.questionnaires import QuestionnaireTemplateBlockFactory
from mystery_shopping.factories.users import UserThatIsTenantProductManagerFactory


class QuestionnaireTemplateBlockAPITestCase(ReadWriteRESTAPITestCaseMixin, BaseRESTAPITestCase):

    base_name = 'questionnairetemplateblock'
    factory_class = QuestionnaireTemplateBlockFactory
    user_factory = UserThatIsTenantProductManagerFactory

    def get_create_data(self):
        # print(self.object.questionnaire_template)
        self.data = json.loads('''{
                               "template_questions":[],
                               "title":"Test Template Block",
                               "weight":"5.00",
                               "parent_block": null
                                }''')
        self.data['parent_block'] = self.object.parent_block.id
        print(type(self.data['parent_block']))
        print(self.object.questionnaire_template.id)
        self.data['questionnaire_template'] = self.object.questionnaire_template.id
        self.data['order'] = self.object.order
        print(self.data)
        return self.data

    def get_update_data(self):
        print(type(self.object.questionnaire_template.id))
        self.data = {'title': 'Updated Title',
                     'questionnaire_template': str(self.object.questionnaire_template.id)}
        return self.data
