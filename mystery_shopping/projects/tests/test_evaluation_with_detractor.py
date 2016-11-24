from django.test.testcases import TestCase
from datetime import datetime
from json import loads, dumps

from mystery_shopping.factories.companies import EntityFactory
from mystery_shopping.factories.projects import ProjectFactory, EvaluationFactory
from mystery_shopping.factories.questionnaires import QuestionnaireTemplateFactory, QuestionnaireScriptFactory
from mystery_shopping.factories.users import ShopperFactory
from mystery_shopping.projects.constants import EvaluationStatus
from mystery_shopping.projects.models import Evaluation
from mystery_shopping.projects.serializers import EvaluationSerializer
from mystery_shopping.users.models import DetractorRespondent


class TestEvaluationWithDetractor(TestCase):
    def setUp(self):
        self.project = ProjectFactory()
        self.shopper = ShopperFactory()
        self.questionnaire_template = QuestionnaireTemplateFactory()
        self.questionnaire_script = QuestionnaireScriptFactory()
        self.entity = EntityFactory()
        self.data = {
            'evaluation_type': 'visit',
            'is_draft': False,
            'suggested_start_date': datetime(2008, 1, 1),
            'suggested_end_date': datetime(2016, 1, 1),
            'status': EvaluationStatus.PLANNED,
            'time_accomplished': None,
            'project': self.project.id,
            'shopper': self.shopper.id,
            'saved_by_user': self.shopper.user.id,
            'questionnaire_script': self.questionnaire_script.id,
            'questionnaire_template': self.questionnaire_template.id,
            'entity': self.entity.id,
            'evaluation_assessment_level': None
        }

    # def test_create_evaluation_with_full_detractor(self):
    #     self.data['detractor_info'] = {
    #         'name': 'Tudor',
    #         'surname': 'Plugaru',
    #         'phone': '+37378166666',
    #         'email': 'demo@demo.com'
    #     }
    #     serializer = EvaluationSerializer(data=self.data)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     self.assertTrue(DetractorRespondent.objects.filter(name='Tudor').exists())
    #     self.assertEqual(DetractorRespondent.objects.get(name='Tudor').evaluation.id, serializer.instance.id)
