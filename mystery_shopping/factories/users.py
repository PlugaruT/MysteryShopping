from datetime import date

import factory
from django.contrib.auth.models import Group
from factory import PostGenerationMethodCall, RelatedFactory, SubFactory, fuzzy
from factory.django import DjangoModelFactory

from mystery_shopping.factories.companies import CompanyElementFactory
from mystery_shopping.factories.tenants import TenantFactory
from mystery_shopping.users.models import ClientUser, Shopper, TenantProjectManager, User
from mystery_shopping.users.roles import UserRole


class TenantProductManagerGroupFactory(DjangoModelFactory):
    class Meta:
        model = Group
        django_get_or_create = ('name',)

    name = UserRole.TENANT_PRODUCT_MANAGER_GROUP


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
        exclude = ('r_password',)

    first_name = factory.Faker('name')
    last_name = factory.Faker('name')
    tenant = SubFactory(TenantFactory)
    date_of_birth = fuzzy.FuzzyDate(date(1990, 1, 12))
    gender = 'f'
    username = fuzzy.FuzzyText(length=10)
    r_password = '1234'
    password = PostGenerationMethodCall('set_password', r_password)
    is_active = True


class ClientUserFactory(DjangoModelFactory):
    class Meta:
        model = ClientUser

    user = SubFactory(UserFactory)
    company = SubFactory(CompanyElementFactory)

    job_title = fuzzy.FuzzyText(length=10)


class TenantProductManagerFactory(DjangoModelFactory):
    class Meta:
        model = User
        exclude = ('r_password',)

    tenant = SubFactory(TenantFactory)


class TenantProjectManagerFactory(DjangoModelFactory):
    class Meta:
        model = TenantProjectManager

    user = SubFactory(UserFactory)
    tenant = SubFactory(TenantFactory)


class ShopperFactory(DjangoModelFactory):
    class Meta:
        model = Shopper

    user = SubFactory(UserFactory)
    has_drivers_license = True


class UserThatIsTenantProductManagerFactory(DjangoModelFactory):
    class Meta:
        model = User
        exclude = ('r_password',)

    tenant = SubFactory(TenantFactory)
    date_of_birth = fuzzy.FuzzyDate(date(1990, 1, 12))
    gender = 'f'
    username = fuzzy.FuzzyText(length=10)
    r_password = '1234'
    password = PostGenerationMethodCall('set_password', r_password)
    is_active = True

    @factory.post_generation
    def groups(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for group in extracted:
                self.groups.add(group)


class UserThatIsTenantProjectManagerFactory(DjangoModelFactory):
    class Meta:
        model = User
        exclude = ('r_password',)

    username = fuzzy.FuzzyText(length=10)
    r_password = '1234'
    password = PostGenerationMethodCall('set_password', r_password)
    is_active = True
    shopper = RelatedFactory(TenantProjectManager, factory_related_name='user')
