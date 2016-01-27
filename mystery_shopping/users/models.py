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
        return 'Tenant Product Manager'


class TenantProjectManager(TenantUserAbstract):
    """The model class for Tenant Project Manager.
    """
    # Relations
    tenant = models.ForeignKey(Tenant, related_name='project_managers')

    def __str__(self):
        return u'{} {}'.format(self.user, self.tenant)

    def get_type(self):
        return 'Tenant Project Manager'


class TenantConsultant(TenantUserAbstract):
    """The model class for Tenant Consultant.
    """
    # Relations
    tenant = models.ForeignKey(Tenant, related_name='consultants')

    def __str__(self):
        return u'{} {}'.format(self.user, self.tenant)

    def get_type(self):
       return 'Tenant Consultant'


class ClientUserAbstract(models.Model):
    """The abstract class for Client User model.

    This class define the common relations and attributes for all Client Users.

    .. note:: The Company relation is not included here for the purpose of defining an explicit related_name
        on each Client User class.
    """
    # Relations
    user = models.OneToOneField(User, null=True)

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
    place  = GenericForeignKey('place_type', 'place_id')

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


class ProjectWorker(models.Model):
    """
    A class with a generic foreign key for setting workers for a project.

    A worker can either be a Tenant Project Manager, or a Tenant Consultant
    """
    limit = models.Q(app_label='users', model='tenantprojectmanager') |\
            models.Q(app_label='users', model='tenantconsultant') |\
            models.Q(app_label='users', model='tenantproductmanager')
    project_worker_type = models.ForeignKey(ContentType, limit_choices_to=limit, related_name='content_type_project_workers')
    project_worker_id = models.PositiveIntegerField()
    project_worker = GenericForeignKey('project_worker_type', 'project_worker_id')


    def __str__(self):
        if self.project_worker_type.model == 'tenantprojectmanager':
            user = TenantProjectManager.objects.get(pk=self.project_worker_id)
        elif self.project_worker_type.model == 'tenantconsultant':
            user= TenantConsultant.objects.get(pk=self.project_worker_id)
        elif self.project_worker_type.model == 'tenantproductmanager':
            user= TenantProductManager.objects.get(pk=self.project_worker_id)
        return 'type: {}, user: {}'.format(self.project_worker_type, user.user.username)


class PersonToAssess(models.Model):
    """
    A class with a generic foreign key for setting people to be evaluated for a project.

    A person to assess can either be a Client Manager or a Client Employee
    """
    limit = models.Q(app_label='users', model='clientmanager') |\
            models.Q(app_label='users', model='clientemployee')
    person_type = models.ForeignKey(ContentType, limit_choices_to=limit, related_name='content_type_person_to_assess')
    person_id = models.PositiveIntegerField()
    person  = GenericForeignKey('person_type', 'person_id')
