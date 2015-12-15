from datetime import date

from factory.django import DjangoModelFactory
from factory import SubFactory
from factory.fuzzy import FuzzyDate

from .companies import CompanyFactory
from .tenants import TenantFactory
from mystery_shopping.factories.users import TenantProjectManagerFactory
from mystery_shopping.projects.models import Project


class ProjectFactory(DjangoModelFactory):
    class Meta:
        model = Project

    tenant = SubFactory(TenantFactory)
    client = SubFactory(CompanyFactory)
    tenant_project_manager = SubFactory(TenantProjectManagerFactory)

    period_start = FuzzyDate(date(1990, 12, 12))
    period_end = FuzzyDate(date(2000, 11, 2))
