from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models

from mystery_shopping.companies.models import Company, Department, Entity, Section
from mystery_shopping.questionnaires.models import QuestionnaireScript, QuestionnaireTemplate
from mystery_shopping.tenants.models import Tenant
from mystery_shopping.questionnaires.models import QuestionnaireTemplate
# from mystery_shopping.users.models import Shopper
# from mystery_shopping.users.models import TenantProjectManager


class PlaceToAssess(models.Model):
    """
    A class with a generic foreign key for setting places to be evaluated for a project.

    A person to assess can either be an Entity or a Section
    """
    limit = models.Q(app_label='companies', model='entity') |\
            models.Q(app_label='companies', model='section')
    content_type = models.ForeignKey(ContentType, limit_choices_to=limit, related_name='content_type_place_to_assess')
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'content_object')


class ResearchMethodology(models.Model):
    """

    """
    # Relations
    # many to many fields
    scripts = models.ManyToManyField(QuestionnaireScript)
    questionnaires = models.ManyToManyField(QuestionnaireTemplate)
    places_to_assess = models.ManyToManyField(PlaceToAssess)
    people_to_assess = models.ManyToManyField('users.PersonToAssess')

    # Attributes
    number_of_evaluations = models.PositiveSmallIntegerField()  # or number_of_calls
    description = models.TextField(blank=True)
    # desired_shopper_profile = models.CharField(max_length="1000")

    class Meta:
        verbose_name_plural = 'research methodologies'
        default_related_name = 'research_methodologies'
        ordering = ('number_of_evaluations',)


class Project(models.Model):
    """

    """
    # Relations
    tenant = models.ForeignKey(Tenant)
    client = models.ForeignKey(Company)
    # this type of import is used to avoid import circles
    tenant_project_manager = models.ForeignKey('users.TenantProjectManager')
    consultants = models.ManyToManyField('users.ProjectWorker')
    shoppers = models.ManyToManyField('users.Shopper')
    research_methodology = models.ForeignKey('ResearchMethodology')

    # Attributes
    period_start = models.DateField()
    period_end = models.DateField()

    class Meta:
        default_related_name = 'projects'
        ordering = ('tenant',)

    def __str__(self):
        return 'Project for {}'.format(self.client.name)


class PlannedEvaluation(models.Model):
    """

    """
    project = models.ForeignKey(Project)
    shopper = models.ForeignKey('users.Shopper')
    questionnaire_script = models.ForeignKey(QuestionnaireScript)
    questionnaire_template = models.ForeignKey(QuestionnaireTemplate)
    entity = models.ForeignKey(Entity)
    section = models.ForeignKey(Section, null=True, blank=True)

    limit = models.Q(app_label='users', model='clientmanager') | \
            models.Q(app_label='users', model='clientemployee')
    employee_type = models.ForeignKey(ContentType, limit_choices_to=limit, related_name='employee_type', null=True, blank=True)
    employee_id = models.PositiveIntegerField(null=True, blank=True)
    employee_object = GenericForeignKey('employee_type', 'employee_id')

    visit_choices = (('call', 'Call'),
                     ('visit', 'Visit'),)
    visit_type = models.CharField(max_length=6, choices=visit_choices)

    class Meta:
        default_related_name = 'planned_evaluations'

    def __str__(self):
        return '{}, shopper: {}'.format(self.project, self.shopper.user.last_name)


class AccomplishedEvaluation(PlannedEvaluation):
    """

    """
    

