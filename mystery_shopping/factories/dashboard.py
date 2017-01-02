from factory.django import DjangoModelFactory
from factory import SubFactory
from datetime import datetime

from factory.helpers import post_generation

from mystery_shopping.dashboard.models import DashboardTemplate
from mystery_shopping.factories.companies import CompanyFactory, CompanyElementFactory
from mystery_shopping.factories.tenants import TenantFactory
from mystery_shopping.factories.users import UserFactory


class DashboardTemplateFactory(DjangoModelFactory):
    class Meta:
        model = DashboardTemplate

    # Relations
    tenant = SubFactory(TenantFactory)
    company_element = SubFactory(CompanyElementFactory)
    company = SubFactory(CompanyFactory)
    modified_by = SubFactory(UserFactory)

    # Attributes
    title = "Dashboard from Factory"
    widgets = "Widget random"
    is_published = True
    modified_date = datetime.now()

    @post_generation
    def users(self, create, users, **kwargs):
        if not create:
            return
        if users:
            for user in users:
                self.users.add(user)

