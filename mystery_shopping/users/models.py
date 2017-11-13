# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db import models
from guardian.shortcuts import get_objects_for_user

from mystery_shopping.companies.models import CompanyElement
from mystery_shopping.mystery_shopping_utils.models import OptionalTenantModel
from mystery_shopping.projects.models import Evaluation, ResearchMethodology
from mystery_shopping.users.roles import UserRole


class User(OptionalTenantModel, AbstractUser):
    # First Name and Last Name do not cover name patterns
    # around the globe.
    phone_number = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, null=True, blank=True)

    def __str__(self):
        return u"{} {}".format(self.first_name, self.last_name)

    def get_absolute_url(self):
        return reverse('users:detail', kwargs={'username': self.username})

    @property
    def user_type(self):
        list_of_groups = self.get_group_names()
        return [UserRole.GROUPS_TO_ROLES[group_name] for group_name in list_of_groups]

    @property
    def user_roles(self):
        roles = self.user_type
        if getattr(self, 'is_staff', False) is True:
            roles.append('admin')
        return roles

    def is_in_group(self, group_name):
        return self.groups.filter(name=group_name).exists()

    def is_in_groups(self, group_names):
        return self.groups.filter(name__in=group_names).exists()

    def get_group_names(self):
        return self.groups.values_list('name', flat=True)

    def is_tenant_product_manager(self):
        return self.is_in_group(UserRole.TENANT_PRODUCT_MANAGER_GROUP)

    def is_tenant_project_manager(self):
        return self.is_in_group(UserRole.TENANT_PROJECT_MANAGER_GROUP)

    def is_tenant_manager(self):
        return self.is_tenant_product_manager() or self.is_tenant_project_manager()

    def is_client_user(self):
        return self.is_in_groups(UserRole.CLIENT_GROUPS)

    def is_tenant_user(self):
        return self.is_in_groups(UserRole.TENANT_GROUPS)

    def is_shopper(self):
        return self.is_in_group(UserRole.SHOPPER_GROUP)

    def is_collector(self):
        return self.is_in_group(UserRole.COLLECTOR_GROUP)

    def user_company(self):
        if self.is_in_groups(UserRole.CLIENT_GROUPS):
            return self.client_user.company
        return None

    def management_permissions(self):
        return get_objects_for_user(self, klass=CompanyElement,
                                    perms=['manager_companyelement']).values_list('id', flat=True)

    def detractors_permissions(self):
        return get_objects_for_user(self, klass=CompanyElement,
                                    perms=['view_detractors_for_companyelement']).values_list('id', flat=True)

    def statistics_permissions(self):
        return get_objects_for_user(self, klass=CompanyElement,
                                    perms=['view_statistics_for_companyelement']).values_list('id', flat=True)

    def coded_causes_permissions(self):
        return get_objects_for_user(self, klass=CompanyElement,
                                    perms=['view_coded_causes_for_companyelement']).values_list('id', flat=True)

    def get_company_elements_permissions(self):
        return {
            'detractor_permissions': self.detractors_permissions(),
            'statistics_permissions': self.statistics_permissions(),
            'coded_causes_permissions': self.coded_causes_permissions(),
            'manager_permissions': self.management_permissions()
        }


class ClientUser(models.Model):
    """Class for Client User model.

    This class define the common relations and attributes for all Client Users.

    """
    # Relations
    user = models.OneToOneField(User, related_name='client_user')
    company = models.ForeignKey(CompanyElement, related_name='client_users')

    job_title = models.CharField(max_length=60, blank=True)

    def __str__(self):
        return u'pk: {}, username: {}'.format(self.id, self.user.username)

    def get_detractor_manager_ids(self):
        return self.user.detractors_manager_projects.all().values_list('id', flat=True)


class Shopper(models.Model):
    """
    A model for the Shopper user
    """
    # Relations
    user = models.OneToOneField(User, related_name='shopper')

    # Attributes
    has_drivers_license = models.BooleanField(default=False)
    address = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return u'pk: {}, name: {},  username: {}'.format(self.id, self.user, self.user.username)


class Collector(models.Model):
    """
    A user model for the persons who will input the NPS questionnaires
    """
    user = models.OneToOneField(User, related_name='collector')

    def __str__(self):
        return u'{}'.format(self.user.username)
