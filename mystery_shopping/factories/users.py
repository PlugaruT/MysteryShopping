from datetime import timedelta

import factory
from django.contrib.auth.models import Group
from django.utils import timezone
from factory import LazyAttribute, PostGenerationMethodCall, SubFactory, fuzzy
from factory.django import DjangoModelFactory
from factory.helpers import post_generation

from mystery_shopping.factories.companies import CompanyElementFactory
from mystery_shopping.factories.tenants import TenantFactory
from mystery_shopping.users.models import ClientUser, Shopper, User
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

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    tenant = SubFactory(TenantFactory)
    date_of_birth = timezone.now().date() - timedelta(days=100)
    gender = 'f'
    username = fuzzy.FuzzyText(length=10)
    email = LazyAttribute(lambda o: '%s@example.org' % o.username)
    r_password = '1234'
    password = PostGenerationMethodCall('set_password', r_password)
    is_active = True

    @post_generation
    def groups(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for group in extracted:
                self.groups.add(group)


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
    date_of_birth = timezone.now().date() - timedelta(days=100)
    gender = 'f'
    username = fuzzy.FuzzyText(length=10)
    r_password = '1234'
    password = PostGenerationMethodCall('set_password', r_password)
    is_active = True

    @post_generation
    def groups(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for group in extracted:
                self.groups.add(group)
