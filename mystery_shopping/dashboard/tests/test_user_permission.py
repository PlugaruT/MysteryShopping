from rest_framework.test import APITestCase
import json

from mystery_shopping.factories.companies import CompanyFactory, CompanyElementFactory
from mystery_shopping.factories.dashboard import DashboardTemplateFactory
from mystery_shopping.users.tests.user_authentication import AuthenticateUser


class TestPermissionsToDashboard(APITestCase):
    def setUp(self):
        self.authenthification = AuthenticateUser()
        self.client = self.authenthification.client
        self.user = self.authenthification.user
        self.company_element = CompanyElementFactory()
        self.company = CompanyFactory()
        self.dashboard1 = DashboardTemplateFactory(title='Dashboard 1', company=self.company)
        self.dashboard2 = DashboardTemplateFactory(title='Dashboard 2', company=self.company)

    def test_if_company_is_set_accordingly_to_dashboard(self):
        response = self.client.get('/api/v1/dashboard/templates/?company={}'.format(self.company.id))
        for dashboard in response.data:
            self.assertEqual(self.company.id, dashboard.get('company'))

    def test_if_modified_by_field_is_set_accordingly(self):
        response = self.client.post('/api/v1/dashboard/templates/?company={}'.format(self.company.id),
                                    data=json.dumps({'title': "demo title",
                                                    'widgets': "something", 'tenant': self.authenthification.tenant.id,
                                                     'company_element': self.company_element.id,
                                                     'company': self.company.id,
                                                     'users': [self.user.id]
                                                    }), content_type='application/json')
        self.assertEqual(self.user.id, response.data.get('modified_by'))

    def test_when_is_publisher_flag_is_false(self):
        self.dashboard2.is_published = False
        self.dashboard2.save()
        response = self.client.get('/api/v1/dashboard/templates/?company={}'.format(self.company.id))
        for dashboard in response.data:
            self.assertTrue(dashboard.get('is_published'))

    def test_when_user_is_tenant_manager_has_access_to_two_dashboards(self):
        self.dashboard1.users.add(self.user)
        self.dashboard2.users.add(self.user)
        response = self.client.get('/api/v1/dashboard/templates/?company={}'.format(self.company.id))
        self.assertEqual(2, len(response.data))

    def test_when_user_is_tenant_manager_and_is_not_assigned_to_any_dashboard(self):
        response = self.client.get('/api/v1/dashboard/templates/?company={}'.format(self.company.id))
        # check if 2 dashboard are sent
        self.assertEqual(2, len(response.data))
        # check that users field is empty
        for dashboard in response.data:
            self.assertListEqual([], dashboard.get('users'))
