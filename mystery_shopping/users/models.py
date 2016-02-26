# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.contrib.auth.models import AbstractUser
from django.core.urlresolvers import reverse
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from mystery_shopping.companies.models import Company
from mystery_shopping.companies.models import Entity
from mystery_shopping.companies.models import Section
from mystery_shopping.projects.models import Project
from mystery_shopping.projects.models import ResearchMethodology
from mystery_shopping.tenants.models import Tenant


# @python_2_unicode_compatible
class User(AbstractUser):

    # First Name and Last Name do not cover name patterns
    # around the globe.
    phone_number = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return u"{}".format(self.username)

    def get_absolute_url(self):
        return reverse('users:detail', kwargs={'username': self.username})

    @property
    def user_type(self):
        if hasattr(self, 'tenantproductmanager'):
            return 'tenantproductmanager'
        elif hasattr(self, 'tenantprojectmanager'):
            return 'tenantprojectmanager'
        elif hasattr(self, 'tenantconsultant'):
            return 'tenantconsultant'
        elif hasattr(self, 'shopper'):
            return 'shopper'
        else:
            return []

    @property
    def user_type_attr(self):
        if hasattr(self, 'tenantproductmanager'):
            return getattr(self, 'tenantproductmanager')
        elif hasattr(self, 'tenantprojectmanager'):
            return getattr(self, 'tenantprojectmanager')
        elif hasattr(self, 'tenantconsultant'):
            return getattr(self, 'tenantconsultant')
        else:
            return None

    @property
    def user_roles(self):
        roles = []
        if hasattr(self, 'tenantproductmanager'):
            roles.append('tenantproductmanager')
        if hasattr(self, 'tenantprojectmanager'):
            roles.append('tenantprojectmanager')
        if hasattr(self, 'tenantconsultant'):
            roles.append('tenantconsultant')
        if hasattr(self, 'shopper'):
            roles.append('shopper')
        if hasattr(self, 'clientprojectmanager'):
            roles.append('clientprojectmanager')
        if hasattr(self, 'clientmanager'):
            roles.append('clientmanager')
        if hasattr(self, 'clientemployee'):
            roles.append('clientemployee')
        return roles

    # TODO: add a get_tenant method
    @property
    def get_tenant(self):
        return self.user_type_attr.tenant


class TenantUserAbstract(models.Model):
    """The abstract class for Tenant User model.

    This class defines the common relations and attributes for all Tenant Users.

    .. note:: The Tenant relation is not included here for the purpose of defining an explicit related_name
        on each Tenant User class.
    """
    # Relations
    user = models.OneToOneField(User)

    class Meta:
        abstract = True
        ordering = ('user',)

    def __str__(self):
        return self.user


class TenantProductManager(TenantUserAbstract):
    """The model class for Tenant Product Manager.
    """
    # Relations
    tenant = models.ForeignKey(Tenant, related_name='product_managers')

    def __str__(self):
        return u'{} {}'.format(self.user, self.tenant)

    def get_type(self):
        return 'tenantproductmanager'


class TenantProjectManager(TenantUserAbstract):
    """The model class for Tenant Project Manager.
    """
    # Relations
    tenant = models.ForeignKey(Tenant, related_name='project_managers')

    def __str__(self):
        return u'{} {}'.format(self.user, self.tenant)

    def get_type(self):
        return 'tenantprojectmanager'


class TenantConsultant(TenantUserAbstract):
    """The model class for Tenant Consultant.
    """
    # Relations
    tenant = models.ForeignKey(Tenant, related_name='consultants')

    def __str__(self):
        return u'{} {}'.format(self.user, self.tenant)

    def get_type(self):
       return 'tenantconsultant'


class ClientUserAbstract(models.Model):
    """The abstract class for Client User model.

    This class define the common relations and attributes for all Client Users.

    .. note:: The Company relation is not included here for the purpose of defining an explicit related_name
        on each Client User class.
    """
    # Relations
    user = models.OneToOneField(User, null=True)
    tenant = models.ForeignKey(Tenant, related_name='%(class)ss')

    # Attributes
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    job_title = models.CharField(max_length=60, blank=True)

    class Meta:
        abstract = True
        ordering = ('user',)

    def __str__(self):
        return self.user


class ClientProjectManager(ClientUserAbstract):
    """The model class for Client Project Manager user.
    """
    # Relations
    company = models.ForeignKey(Company, related_name='project_managers')

    def __str__(self):
        return u'{} {}'.format(self.user, self.company)


class ClientManager(ClientUserAbstract):
    """The model class for Client Manager user.

    Client Manager can have several types of entities that he/she can manage, which are: Department, Entity or Section.
    """
    # Relations
    company = models.ForeignKey(Company, related_name='managers')
    limit = models.Q(app_label='companies', model='department') |\
            models.Q(app_label='companies', model='entity') |\
            models.Q(app_label='companies', model='section')
    place_type = models.ForeignKey(ContentType, limit_choices_to=limit, related_name='place_type', null=True, blank=True)
    place_id = models.PositiveIntegerField(null=True, blank=True)
    place = GenericForeignKey('place_type', 'place_id')

    def __str__(self):
        return u'{} {}'.format(self.user, self.place)


class ClientEmployee(ClientUserAbstract):
    """The model class for Client Employee user.
    """
    # Relations
    company = models.ForeignKey(Company)
    entity = models.ForeignKey(Entity)
    section = models.ForeignKey(Section, null=True)

    class Meta(ClientUserAbstract.Meta):
        default_related_name = 'employees'

    def __str__(self):
        return u'{} {} {}'.format(self.user, self.company, self.entity)


class Shopper(models.Model):
    """
    A model for the Shopper user
    """
    # Relations
    user = models.OneToOneField(User, related_name='shopper')
    # Attributes
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1)
    has_drivers_license = models.BooleanField(default=False)

    def __str__(self):
        return u'{}'.format(self.user.username)


class PersonToAssess(models.Model):
    """
    A class with a generic foreign key for setting people to be evaluated for a project.

    A person to assess can either be a Client Manager or a Client Employee
    """
    limit = models.Q(app_label='users', model='clientmanager') |\
            models.Q(app_label='users', model='clientemployee')
    person_type = models.ForeignKey(ContentType, limit_choices_to=limit, related_name='content_type_person_to_assess')
    person_id = models.PositiveIntegerField()
    person = GenericForeignKey('person_type', 'person_id')

    research_methodology = models.ForeignKey(ResearchMethodology, related_name='people_to_assess')
