from factory.django import DjangoModelFactory
from factory import fuzzy, Sequence, SubFactory, PostGenerationMethodCall
from faker import Factory

from ..models import Company, Industry, Department, Entity, Section
from mystery_shopping.common.models import Country, CountryRegion, County, City, Sector
from mystery_shopping.users.models import User, TenantProductManager, TenantProjectManager
from mystery_shopping.tenants.models import Tenant


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
        exclude = ('r_password',)

    username = fuzzy.FuzzyText(length=10)
    r_password = '1234'
    password = PostGenerationMethodCall('set_password', r_password)
    is_active = True


class TenantFactory(DjangoModelFactory):
    class Meta:
        model = Tenant

    name = Sequence(lambda n: "Tenant {0}".format(n))


class TenantProductManagerFactory(DjangoModelFactory):
    class Meta:
        model = TenantProductManager

    user = SubFactory(UserFactory)
    tenant = SubFactory(TenantFactory)


class TenantProjectManagerFactory(DjangoModelFactory):
    class Meta:
        model = TenantProjectManager

    user = SubFactory(UserFactory)
    tenant = SubFactory(TenantFactory)


class CountryFactory(DjangoModelFactory):
    class Meta:
        model = Country

    name = fuzzy.FuzzyText(length=15)


class CountryRegionFactory(DjangoModelFactory):
    class Meta:
        model = CountryRegion

    name = fuzzy.FuzzyText(length=20)


class CountyFactory(DjangoModelFactory):
    class Meta:
        model = County

    country = SubFactory(CountryFactory)
    country_region = SubFactory(CountryRegionFactory)

    name = fuzzy.FuzzyText(length=20)


class CityFactory(DjangoModelFactory):
    class Meta:
        model = City

    county = SubFactory(CountyFactory)
    name = fuzzy.FuzzyText(length=10)


class SectorFactory(DjangoModelFactory):
    class Meta:
        model = Sector

    city = SubFactory(CityFactory)
    name = fuzzy.FuzzyText(length=10)


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
        model = Department

    entity = SubFactory(EntityFactory)
    tenant = SubFactory(TenantFactory)

    name = "The Carpet"
