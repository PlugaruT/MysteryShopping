from datetime import datetime

from django.test.testcases import TestCase

from mystery_shopping.factories.companies import CompanyElementFactory
from mystery_shopping.factories.projects import ProjectFactory
from mystery_shopping.factories.questionnaires import QuestionnaireScriptFactory, QuestionnaireTemplateFactory
from mystery_shopping.factories.tenants import TenantFactory
from mystery_shopping.factories.users import UserFactory
from mystery_shopping.projects.constants import EvaluationStatus
from mystery_shopping.projects.models import Evaluation
from mystery_shopping.projects.serializers import EvaluationSerializer, EvaluationSerializerGET
from mystery_shopping.users.models import DetractorRespondent


class TestEvaluationWithDetractor(TestCase):
    def setUp(self):
        self.tenant = TenantFactory()
        self.company_element = CompanyElementFactory(tenant=self.tenant)
        self.project = ProjectFactory(tenant=self.tenant, company=self.company_element)
        self.saved_by = UserFactory(tenant=self.tenant)
        self.shopper = UserFactory(tenant=self.tenant)
        self.questionnaire_template = QuestionnaireTemplateFactory()
        self.questionnaire_script = QuestionnaireScriptFactory()
        self.data = {
            'evaluation_type': 'visit',
            'is_draft': False,
            'suggested_start_date': datetime(2008, 1, 1),
            'suggested_end_date': datetime(2016, 1, 1),
            'status': EvaluationStatus.PLANNED,
            'time_accomplished': None,
            'project': self.project.id,
            'shopper': self.shopper.id,
            'saved_by_user': self.saved_by.id,
            'questionnaire_script': self.questionnaire_script.id,
            'questionnaire_template': self.questionnaire_template.id,
            'company_element': self.company_element.pk,
            'evaluation_assessment_level': None
        }
        self.evaluation = EvaluationSerializer(data=self.data)
        self.evaluation.is_valid(raise_exception=True)
        self.evaluation.save()

    # fuck this test
    def _test_create_evaluation_with_detractor(self):
        detractor_info = {
            'name': 'Tudor',
            'surname': 'Plugaru',
            'phone': '+37378166666',
            'email': 'demo@demo.com'
        }
        evaluation = Evaluation.objects.get(pk=self.evaluation.instance.id)
        serializer = EvaluationSerializerGET(evaluation)
        serializer_data = serializer.data
        print(serializer_data.get('questionnaire'))

        serializer_data['detractor_info'] = detractor_info
        serializer = EvaluationSerializer(evaluation, data=dict(serializer_data))
        serializer.is_valid(raise_exception=True)
        serializer.save()

        self.assertTrue(DetractorRespondent.objects.filter(name=detractor_info['name']).exists())
        self.assertEqual(DetractorRespondent.objects.get(name=detractor_info['name']).evaluation.id,
                         serializer.instance.id)
