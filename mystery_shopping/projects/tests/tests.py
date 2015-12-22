from datetime import date
from rest_assured.testcases import ReadWriteRESTAPITestCaseMixin, BaseRESTAPITestCase

from mystery_shopping.factories.projects import ProjectFactory


class ProjectAPITestCase(ReadWriteRESTAPITestCaseMixin, BaseRESTAPITestCase):

    base_name = 'project'
    factory_class = ProjectFactory
    update_date = date.today()
    # TODO check why it doesn't take a string for date update
    update_data = {"period_end": update_date}

    def get_create_data(self):
        return {
            "period_start": "1200-03-30",
            "period_end": "1200-04-03",
            "tenant": self.object.tenant.pk,
            "client": self.object.client.pk,
            "tenant_project_manager": self.object.tenant_project_manager.pk
        }
