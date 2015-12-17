from rest_assured.testcases import ReadWriteRESTAPITestCaseMixin, BaseRESTAPITestCase

from mystery_shopping.factories.users import TenantProjectManagerFactory
from mystery_shopping.factories.users import UserFactory


class TenantProjectManagerAPITestCase(ReadWriteRESTAPITestCaseMixin, BaseRESTAPITestCase):

    base_name = 'tenantprojectmanager'
    factory_class = TenantProjectManagerFactory

    def get_create_data(self):
        return {
            "tenant": self.object.tenant.pk,
            "user": self.object.user.pk
        }

    def get_update_data(self):
        new_user = UserFactory()
        return {
            "user": str(new_user.pk)
        }
