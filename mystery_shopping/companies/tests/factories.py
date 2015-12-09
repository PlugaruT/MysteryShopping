from factory.django import DjangoModelFactory
from factory import fuzzy, Sequence
from faker import Factory

from ..models import Company, Industry
from mystery_shopping.common.models import Country
from mystery_shopping.users.models import User, TenantProductManager, TenantProjectManager
from mystery_shopping.tenants.models import Tenant


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = fuzzy.FuzzyText(length=10)
    password = '1234'


class TenantFactory(DjangoModelFactory):
    class Meta:
        model = Tenant

    name = Sequence(lambda n: "Tenant {0}".format(n))


class TenantProductManagerFactory(DjangoModelFactory):
    class Meta:
        model = TenantProductManager


class TenantProjectManagerFactory(DjangoModelFactory):
    class Meta:
        model = TenantProjectManager


class CountryFactory(DjangoModelFactory):
    class Meta:
        model = Country

    name = fuzzy.FuzzyText(length=15)


class IndustryFactory(DjangoModelFactory):
    class Meta:
        model = Industry

    name = fuzzy.FuzzyText(length=15)


class CompanyFactory(DjangoModelFactory):
    class Meta:
        model = Company

    fake = Factory.create()

    contact_person = fake.name()
    contact_phone = '123'
    contact_email = fake.email()
    domain = 'fsadfsf'
