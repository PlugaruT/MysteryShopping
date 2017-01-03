from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from mystery_shopping.companies.models import CompanyElement
from mystery_shopping.factories.companies import CompanyElementFactory
from mystery_shopping.users.tests.user_authentication import AuthenticateUser


class CompanyElementCloneAPITestCase(APITestCase):
    def setUp(self):
        self.authentification = AuthenticateUser()
        self.client = self.authentification.client
        self.company_element_1 = CompanyElementFactory(tenant=self.authentification.tenant)

    def test_clone_one_company_element(self):
        response = self.client.post(reverse('companyelement-clone', args=(self.company_element_1.id,)))
        new_element = CompanyElement.objects.filter(element_name=self.company_element_1.element_name + ' ('
                                                                                                       'copy)').first()
        self.assertTrue(new_element)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(self.company_element_1.parent, new_element.parent)
        self.assertEqual(self.company_element_1.children.count(), new_element.children.count())

    def test_clone_company_element_with_two_children(self):
        new_name = 'Parent two'
        self.company_element_1.element_name = new_name
        self.company_element_1.save()
        company_element_2 = CompanyElementFactory(parent=self.company_element_1, element_name='child 1')
        company_element_3 = CompanyElementFactory(parent=self.company_element_1, element_name='child 2')
        response = self.client.post(reverse('companyelement-clone', args=(self.company_element_1.id,)))
        new_element = CompanyElement.objects.filter(element_name=self.company_element_1.element_name + ' ('
                                                                                                       'copy)').first()
        self.assertTrue(new_element)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(self.company_element_1.parent, new_element.parent)
        self.assertEqual(self.company_element_1.children.count(), new_element.children.count())
        for child in new_element.children.all():
            self.assertEqual(child.parent.id, new_element.id)

    def test_clone_company_element_with_three_level_children(self):
        new_name = 'Parent three'
        self.company_element_1.element_name = new_name
        self.company_element_1.save()
        company_element_2 = CompanyElementFactory(parent=self.company_element_1, element_name='child 1')
        company_element_3 = CompanyElementFactory(parent=company_element_2, element_name='child 2')
        response = self.client.post(reverse('companyelement-clone', args=(self.company_element_1.id,)))
        new_element = CompanyElement.objects.filter(element_name=self.company_element_1.element_name + ' ('
                                                                                                       'copy)').first()
        self.assertTrue(new_element)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(self.company_element_1.parent, new_element.parent)
        self.assertEqual(self.company_element_1.children.count(), new_element.children.count())
        for child in new_element.children.all():
            self.assertEqual(child.parent.id, new_element.id)
            for c in child.children.all():
                self.assertEqual(c.parent.id, child.id)
