from django.db import models

# Create your models here.
from rest_framework.filters import BaseFilterBackend

from mystery_shopping.tenants.models import Tenant


class TenantModel(models.Model):
    """
    Generic abstract class model that has a reference to a `tenant`
    and some helpful methods on `tenant` handling.
    """
    tenant = models.ForeignKey(Tenant)

    class Meta:
        abstract = True


class OptionalTenantModel(models.Model):
    """
    Generic abstract class model that has a reference to a `tenant`
    and some helpful methods on `tenant` handling.
    """
    tenant = models.ForeignKey(Tenant, null=True, blank=True)

    class Meta:
        abstract = True


class TenantFilter(BaseFilterBackend):
    """
    Generic Filter to use on all views whose models have a tenant
     reference.
    """
    def filter_queryset(self, request, queryset, view):
        return queryset.filter(tenant=request.user.tenant)
