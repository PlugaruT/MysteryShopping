from rest_assured.testcases import ReadWriteRESTAPITestCaseMixin, BaseRESTAPITestCase

from mystery_shopping.factories.users import ShopperFactory
from mystery_shopping.factories.users import UserThatIsTenantProjectManagerFactory


class ShopperAPITestCase(ReadWriteRESTAPITestCaseMixin, BaseRESTAPITestCase):

    base_name = 'shopper'
    factory_class = ShopperFactory
    user_factory = UserThatIsTenantProjectManagerFactory
    update_data = {'gender': 'm'}

    def get_create_data(self):
        return {
            "user": self.object.user.pk,
            "date_of_birth": "1990-01-12",
            "gender": "f",
            "has_drivers_license": True
        }