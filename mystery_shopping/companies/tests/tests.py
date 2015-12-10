from rest_assured.testcases import ReadWriteRESTAPITestCaseMixin, BaseRESTAPITestCase

from . import factories


class CompanyAPITestWithTProjManagerTestCase(ReadWriteRESTAPITestCaseMixin, BaseRESTAPITestCase):

    base_name = 'company'
    factory_class = factories.CompanyFactory
    user_factory = factories.TenantProjectManagerFactory
    update_data = {'name': 'Best company'}


    # def setUp(self):
    #     factories.

    def get_create_data(self):
        # data['industry'] = self.
        return {
            "name": "Papuci SRL",
            "contact_person": "Mircea Papuc",
            "contact_phone": "1234",
            "contact_email": "mircea@papuc.pa",
            "domain": "papuci",
            "industry": self.object.industry.pk,
            "country": self.object.country.pk,
            "tenant": self.object.tenant.pk
        }