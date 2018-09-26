from factory import SubFactory, fuzzy
from factory.django import DjangoModelFactory

from mystery_shopping.companies.models import CompanyElement, Industry
from mystery_shopping.factories.tenants import TenantFactory

#test
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
