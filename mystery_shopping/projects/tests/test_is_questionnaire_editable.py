from django.test.testcases import TestCase

from mystery_shopping.factories.projects import ResearchMethodologyFactory, ProjectFactory, EvaluationFactory
from mystery_shopping.factories.questionnaires import QuestionnaireTemplateFactory, QuestionnaireFactory
from mystery_shopping.factories.tenants import TenantFactory
from mystery_shopping.projects.serializers import ProjectSerializer, ProjectSerializerGET


class TestQuestionnaireIsEditable(TestCase):
    def setUp(self):
        self.tenant = TenantFactory()
        self.template_questionnaire = QuestionnaireTemplateFactory()
        self.questionnaire = QuestionnaireFactory(template=self.template_questionnaire)
        self.research_methodology = ResearchMethodologyFactory()
        self.research_methodology.questionnaires.add(self.template_questionnaire)
        self.project = ProjectFactory(tenant=self.tenant, research_methodology=self.research_methodology)

    def test_flag_when_there_is_one_evaluation(self):
        EvaluationFactory(project=self.project,
                          questionnaire=self.questionnaire,
                          questionnaire_template=self.template_questionnaire)
        self.project.refresh_from_db()
        serializer = ProjectSerializerGET(self.project)
        self.assertFalse(serializer.data.get('is_questionnaire_editable'))

    def test_flag_when_there_are_no_evaluations(self):
        serializer = ProjectSerializerGET(self.project)

        self.assertTrue(serializer.data.get('is_questionnaire_editable'))
