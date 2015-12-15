from factory.django import DjangoModelFactory
from factory import fuzzy, Sequence, SubFactory, PostGenerationMethodCall
from faker import Factory

from .tenants import TenantFactory
from mystery_shopping.users.models import User, TenantProductManager, TenantProjectManager


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
        exclude = ('r_password',)

    username = fuzzy.FuzzyText(length=10)
    r_password = '1234'
    password = PostGenerationMethodCall('set_password', r_password)
    is_active = True


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
