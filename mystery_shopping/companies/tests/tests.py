from rest_assured.testcases import ReadWriteRESTAPITestCaseMixin, BaseRESTAPITestCase

from mystery_shopping.factories.users import TenantProjectManagerFactory
from mystery_shopping.factories.companies import CompanyFactory
from mystery_shopping.factories.users import UserThatIsTenantProductManagerFactory


# class CompanyAPITestWithTProjManagerTestCase(ReadWriteRESTAPITestCaseMixin, BaseRESTAPITestCase):
#
#     base_name = 'company'
#     factory_class = CompanyFactory
#     user_factory = UserThatIsTenantProductManagerFactory
#     update_data = {'name': 'Best company'}
#
#     def get_create_data(self):
#         return {
#             "name": "Papuci SRL",
#             "contact_person": "Mircea Papuc",
#             "contact_phone": "1234",
#             "contact_email": "mircea@papuc.pa",
#             "domain": "papuci",
#             "industry": self.object.industry.pk,
#             "country": self.object.country.pk,
#             "tenant": self.object.tenant.pk
#         }