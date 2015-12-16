from rest_assured.testcases import ReadWriteRESTAPITestCaseMixin, BaseRESTAPITestCase

from mystery_shopping.factories.tenants import Tenant
from mystery_shopping.factories.users import TenantProjectManagerFactory, ProjectWorkerTenantProjectManagerFactory


class ProjectWorkerAPITestCase(ReadWriteRESTAPITestCaseMixin, BaseRESTAPITestCase):

    base_name = 'projectworker'
    factory_class = ProjectWorkerTenantProjectManagerFactory

    def get_create_data(self):
        return {
            "content_object": self.object.object_content.pk
        }

    def get_update_data(self):
        tenant_project_manager = TenantProjectManagerFactory()
        return {
            "content_object": tenant_project_manager.pk
        }