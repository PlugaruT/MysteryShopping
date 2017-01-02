from factory.django import DjangoModelFactory
from factory import fuzzy, Sequence, SubFactory, PostGenerationMethodCall

from .common import CountryFactory, CityFactory, SectorFactory
from .tenants import TenantFactory
from mystery_shopping.companies.models import Company, Industry, Department, Entity, Section, CompanyElement


class IndustryFactory(DjangoModelFactory):
    class Meta:
        model = Industry

    name = fuzzy.FuzzyText(length=15)


class CompanyFactory(DjangoModelFactory):
    class Meta:
        model = Company

    # fake = Factory.create()

    industry = SubFactory(IndustryFactory)
    country = SubFactory(CountryFactory)
    tenant = SubFactory(TenantFactory)

    contact_person = "fdsafs"  # fake.name()
    contact_phone = '123'
    contact_email = "fdsfsfas@fasd.com"  # fake.email()
    domain = 'fsadfsf'


class DepartmentFactory(DjangoModelFactory):
    class Meta:
        model = Department

    company = SubFactory(CompanyFactory)
    tenant = SubFactory(TenantFactory)

    name = fuzzy.FuzzyText(length=20)


class EntityFactory(DjangoModelFactory):
    class Meta:
        model = Entity

    department = SubFactory(DepartmentFactory)
    city = SubFactory(CityFactory)
    sector = SubFactory(SectorFactory)
    tenant = SubFactory(TenantFactory)

    name = "Aladeen"
    address = "79665 Brekke Prairie Suite 508"
    coordinates = "lat: 38.706863 long: -90.298205"


class SectionFactory(DjangoModelFactory):
    class Meta:
        model = Section

    entity = SubFactory(EntityFactory)
    tenant = SubFactory(TenantFactory)

    name = "The Carpet"


class CompanyElementFactory(DjangoModelFactory):
    class Meta:
        model = CompanyElement

    additional_info = {}
    element_name = 'Default name'
    element_type = 'Default type'
    logo = None
    parent = None
    tenant = SubFactory(TenantFactory)
