from rest_assured.testcases import ReadWriteRESTAPITestCaseMixin, BaseRESTAPITestCase

from mystery_shopping.factories.users import TenantProjectManagerFactory
from mystery_shopping.factories.users import UserFactory
from mystery_shopping.factories.users import UserThatIsTenantProductManagerFactory
import pdb


# class TenantProjectManagerAPITestCase(ReadWriteRESTAPITestCaseMixin, BaseRESTAPITestCase):
#
#     base_name = 'tenantprojectmanager'
#     user_factory = UserThatIsTenantProductManagerFactory
#     factory_class = TenantProjectManagerFactory
#     content_type = 'application/json'
#
#     def get_create_data(self):
#         pdb.set_trace()
#         data = {
#             "tenant": self.object.tenant.pk,
#             "user": self.object.user.pk
#         }
#         print(data)
#         return data
#
#     def get_create_response(self, data=None, **kwargs):
#         """Send the create request and return the response.
#
#         :param data: A dictionary of the data to use for the create request.
#         :param kwargs: Extra arguments that are passed to the client's ``post()`` call.
#         :returns: The response object.
#         """
#
#         kwargs['content_type'] = self.content_type
#
#         if data is None:
#             data = self.get_create_data()
#
#         return self.client.post(self.get_create_url(), data or {}, **kwargs)
#
#     def get_update_data(self):
#         new_user = UserFactory()
#         return {
#             "user": str(new_user.pk)
#         }
