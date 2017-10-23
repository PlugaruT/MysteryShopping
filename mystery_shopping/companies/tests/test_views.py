from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from mystery_shopping.companies.models import CompanyElement
from mystery_shopping.factories.companies import CompanyElementFactory
from mystery_shopping.factories.projects import ProjectFactory, ResearchMethodologyFactory, EvaluationFactory
from mystery_shopping.factories.tenants import TenantFactory
from mystery_shopping.factories.users import UserFactory
from mystery_shopping.users.tests.user_authentication import AuthenticateUser


class CompanyElementAPITestCase(APITestCase):
    def setUp(self):
        self.tenant = TenantFactory()
        self.authentication = AuthenticateUser(tenant=self.tenant)
        self.client = self.authentication.client
        self.company = CompanyElementFactory(tenant=self.tenant)
        self.company_element = CompanyElementFactory(tenant=self.tenant, parent=self.company)
        self.user = UserFactory()
        self.research_methodology = ResearchMethodologyFactory(tenant=self.tenant)
        self.research_methodology.company_elements.add(self.company_element)
        self.project = ProjectFactory(tenant=self.tenant, company=self.company, project_manager=self.user)
        self.evaluation = EvaluationFactory(project=self.project)

    def test_delete_company_element_with_no_evaluations(self):
        response = self.client.delete(reverse('companyelement-detail', args=(self.company_element.id,)))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, response.data)
        self.assertRaises(ObjectDoesNotExist, CompanyElement.objects.get, id=self.company_element.id)

    def test_delete_company_element_with_evaluations(self):
        self.evaluation.company_element = self.company_element
        self.evaluation.save()
        response = self.client.delete(reverse('companyelement-detail', args=(self.company_element.id,)))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
