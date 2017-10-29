from factory.django import DjangoModelFactory
from factory import fuzzy, Sequence, SubFactory, PostGenerationMethodCall

from .common import CountryFactory, CityFactory, SectorFactory
from .tenants import TenantFactory
from mystery_shopping.companies.models import Industry, CompanyElement


class IndustryFactory(DjangoModelFactory):
    class Meta:
        model = Industry

    name = fuzzy.FuzzyText(length=15)


class CompanyElementFactory(DjangoModelFactory):
    class Meta:
        model = CompanyElement

    additional_info = {}
    element_name = 'Default name'
    element_type = 'Default type'
    logo = None
    parent = None
    tenant = SubFactory(TenantFactory)
