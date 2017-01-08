from django.contrib.contenttypes.models import ContentType
from django.test.testcases import TestCase

from mystery_shopping.factories.companies import CompanyElementFactory
from mystery_shopping.factories.projects import EvaluationFactory, ProjectFactory, ResearchMethodologyFactory
from mystery_shopping.factories.questionnaires import QuestionnaireTemplateFactory
from mystery_shopping.factories.tenants import TenantFactory
from mystery_shopping.projects.serializers import ProjectSerializer, ProjectSerializerGET


class TestProjectEditablePlaces(TestCase):
    def setUp(self):
        self.tenant = TenantFactory()
        self.company_element_1 = CompanyElementFactory(tenant=self.tenant)
        self.company_element_2 = CompanyElementFactory(tenant=self.tenant)
        self.template_questionnaire = QuestionnaireTemplateFactory()
        self.research_methodology = ResearchMethodologyFactory(tenant=self.tenant)
        self.research_methodology.questionnaires.add(self.template_questionnaire)

        self.research_methodology.company_elements.set([self.company_element_1, self.company_element_2])

        self.project = ProjectFactory(tenant=self.tenant, research_methodology=self.research_methodology)

    def test_create_evaluation_for_one_entity(self):
        EvaluationFactory(company_element=self.company_element_1, project=self.project,
                          questionnaire_template=self.template_questionnaire)

        # The list should contain information about self.company_element_2
        self.assertEqual(self.project.get_editable_places(), [self.company_element_2.id])

    def test_create_evaluation_for_two_entities(self):
        EvaluationFactory(company_element=self.company_element_1, project=self.project,
                          questionnaire_template=self.template_questionnaire)
        EvaluationFactory(company_element=self.company_element_2, project=self.project,
                          questionnaire_template=self.template_questionnaire)

        # The list should be empty because there are evaluations for each all entities
        self.assertListEqual(self.project.get_editable_places(), [])

    def test_when_there_are_no_evaluations_for_any_entity(self):
        # Check if the list contains information about 2 entities
        self.assertEqual(len(self.project.get_editable_places()), 2)
        # The list should contain information about all entities because there are no evaluation for them
        self.assertCountEqual(self.project.get_editable_places(),
                              [self.company_element_1.id, self.company_element_2.id])
