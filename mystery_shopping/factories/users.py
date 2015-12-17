from datetime import date

from factory.django import DjangoModelFactory
from factory import fuzzy, Sequence, SubFactory, PostGenerationMethodCall
from faker import Factory

from .tenants import TenantFactory
from mystery_shopping.users.models import User, TenantProductManager, TenantProjectManager, ProjectWorker, Shopper


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


class ProjectWorkerTenantProjectManagerFactory(DjangoModelFactory):
    class Meta:
        model = ProjectWorker

    content_object = SubFactory(TenantProjectManagerFactory)


class ShopperFactory(DjangoModelFactory):
    class Meta:
        model = Shopper

    user = SubFactory(UserFactory)
    date_of_birth = fuzzy.FuzzyDate(date(1990, 1, 12))
    gender = 'f'
    has_car = True
