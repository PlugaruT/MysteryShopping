from unittest.mock import patch

from django.core import mail
from django.test.testcases import TestCase

from mystery_shopping.factories.projects import EvaluationFactory, ProjectFactory
from mystery_shopping.factories.questionnaires import QuestionnaireFactory, QuestionnaireTemplateFactory
from mystery_shopping.factories.tenants import TenantFactory
from mystery_shopping.factories.users import UserFactory
from mystery_shopping.projects.models import Evaluation
from mystery_shopping.projects.serializers import EvaluationSerializer
from mystery_shopping.users.models import DetractorRespondent


class TestEvaluationWithDetractor(TestCase):
    def setUp(self):
        tenant = TenantFactory()
        self.detractors_manager = UserFactory(tenant=tenant)
        project = ProjectFactory(tenant=tenant, detractors_manager=self.detractors_manager)
        questionnaire_template = QuestionnaireTemplateFactory(tenant=tenant)
        questionnaire = QuestionnaireFactory(template=questionnaire_template)
        self.evaluation = EvaluationFactory(project=project, questionnaire=questionnaire)
        self.detractor_info = {
            'name': 'Valera',
            'surname': 'Antonov',
            'phone': '+123123123',
            'email': 'demo@demo.com'
        }

    def test_set_detractor_to_evaluation(self):
        self._add_detractor_to_evaluation()

        detractor = DetractorRespondent.objects.get(**self.detractor_info)

        self.assertEqual(self.evaluation.id, detractor.evaluation.id)

    @patch('mystery_shopping.projects.models.Evaluation.number_of_detractor_questions')
    def test_send_email_if_respondent_is_detractor(self, number_of_detractor_questions):
        number_of_detractor_questions.return_value = 1

        self._add_detractor_to_evaluation()

        self.assertEqual(1, len(mail.outbox))
        self.assertListEqual([self.detractors_manager.email], mail.outbox[0].to)

    @patch('mystery_shopping.projects.models.Evaluation.number_of_detractor_questions')
    def test_send_email_if_respondent_is_not_detractor(self, number_of_detractor_questions):
        number_of_detractor_questions.return_value = 0

        self._add_detractor_to_evaluation()

        self.assertEqual(0, len(mail.outbox))
        self.assertListEqual([], mail.outbox)

    def _add_detractor_to_evaluation(self):
        evaluation = Evaluation.objects.get(pk=self.evaluation.id)
        serializer_data = EvaluationSerializer(evaluation).data
        serializer_data['detractor_info'] = self.detractor_info
        self._update_evaluation(evaluation, serializer_data)

    @staticmethod
    def _update_evaluation(evaluation_instance, serialized_data):
        serializer = EvaluationSerializer(evaluation_instance, data=dict(serialized_data))
        serializer.is_valid(raise_exception=True)
        serializer.save()
