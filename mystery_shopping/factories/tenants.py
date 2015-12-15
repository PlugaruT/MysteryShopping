from factory.django import DjangoModelFactory
from factory import Sequence

from mystery_shopping.tenants.models import Tenant


class TenantFactory(DjangoModelFactory):
    class Meta:
        model = Tenant

    name = Sequence(lambda n: "Tenant {0}".format(n))
