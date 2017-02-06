# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.contrib.auth.models import AbstractUser
from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator
from django.db import models
from guardian.shortcuts import get_objects_for_user
from model_utils import Choices
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from mystery_shopping.companies.models import Company, CompanyElement
from mystery_shopping.companies.models import Entity
from mystery_shopping.companies.models import Section
from mystery_shopping.mystery_shopping_utils.models import OptionalTenantModel
from mystery_shopping.projects.models import Project, Evaluation
from mystery_shopping.projects.models import ResearchMethodology
from mystery_shopping.tenants.models import Tenant

# @python_2_unicode_compatible
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


class ClientUserAbstract(models.Model):
    """The abstract class for Client User model.

    This class define the common relations and attributes for all Client Users.

    .. note:: The Company relation is not included here for the purpose of defining an explicit related_name
        on each Client User class.
    """
    # Relations
    user = models.OneToOneField(User, null=True)
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
    limit = models.Q(app_label='companies', model='department') | \
            models.Q(app_label='companies', model='entity') | \
            models.Q(app_label='companies', model='section')
    place_type = models.ForeignKey(ContentType, limit_choices_to=limit, related_name='place_type', null=True,
                                   blank=True)
    place_id = models.PositiveIntegerField(null=True, blank=True)
    place = GenericForeignKey('place_type', 'place_id')

    # Attributes
    has_overview_access = models.BooleanField(default=False)

    def __str__(self):
        return u'{} {}'.format(self.user, self.place)

    def has_evaluations(self):
        return PersonToAssess.objects.filter(person_id=self.id,
                                             person_type=ContentType.objects.get_for_model(self)).exists()


class ClientEmployee(ClientUserAbstract):
    """
    The model class for Client Employee user.
    """
    # Relations
    company = models.ForeignKey(Company)
    entity = models.ForeignKey(Entity)
    section = models.ForeignKey(Section, null=True)

    class Meta(ClientUserAbstract.Meta):
        default_related_name = 'employees'

    def __str__(self):
        return u'{} {} {}'.format(self.user, self.company, self.entity)

    def has_evaluations(self):
        return PersonToAssess.objects.filter(person_id=self.id,
                                             person_type=ContentType.objects.get_for_model(self)).exists()


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


class PersonToAssess(models.Model):
    """
    A class with a generic foreign key for setting people to be evaluated for a project.

    A person to assess can either be a Client Manager or a Client Employee
    """
    limit = models.Q(app_label='users', model='clientmanager') | \
            models.Q(app_label='users', model='clientemployee')
    person_type = models.ForeignKey(ContentType, limit_choices_to=limit, related_name='content_type_person_to_assess')
    person_id = models.PositiveIntegerField()
    person = GenericForeignKey('person_type', 'person_id')

    research_methodology = models.ForeignKey(ResearchMethodology, related_name='people_to_assess')


class DetractorRespondent(models.Model):
    """
        Model for storing information about detractors of an evaluation.
    """
    name = models.CharField(max_length=20, blank=True)
    surname = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    comment = models.CharField(max_length=400, blank=True)
    additional_comment = models.CharField(max_length=400, blank=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone = models.CharField(validators=[phone_regex], blank=True, max_length=15)
    status_choices = Choices(('TO_CONTACT', 'To Contact'),
                             ('CALL_BACK', 'Call Back'),
                             ('CONTACTED', 'Contacted'))
    status = models.CharField(max_length=11, choices=status_choices, default='TO_CONTACT')

    evaluation = models.ForeignKey(Evaluation, related_name='detractors', null=True)
    number_of_questions = models.IntegerField(default=0)

    def __str__(self):
        return u'{} {}'.format(self.name, self.surname)

    def get_detractor_questions(self):
        return self.evaluation.questionnaire.get_indicator_questions()

    def get_visited_place(self):
        return self.evaluation.company_element
