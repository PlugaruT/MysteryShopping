from factory.django import DjangoModelFactory
from factory import fuzzy, Sequence, SubFactory, PostGenerationMethodCall
from faker import Factory

from ..models import Company, Industry
from mystery_shopping.common.models import Country
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
