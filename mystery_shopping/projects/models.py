from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from model_utils import Choices
from model_utils.models import TimeStampedModel

from mystery_shopping.companies.models import Company, Department, Entity, Section
from mystery_shopping.questionnaires.models import QuestionnaireScript, QuestionnaireTemplate
from mystery_shopping.tenants.models import Tenant
from mystery_shopping.questionnaires.models import QuestionnaireTemplate
from mystery_shopping.questionnaires.models import Questionnaire
# from mystery_shopping.users.models import Shopper
# from mystery_shopping.users.models import TenantProjectManager


class PlaceToAssess(models.Model):
    """
    A class with a generic foreign key for setting places to be evaluated for a project.

    A person to assess can either be an Entity or a Section
    """
    limit = models.Q(app_label='companies', model='entity') |\
            models.Q(app_label='companies', model='section')
    place_type = models.ForeignKey(ContentType, limit_choices_to=limit, related_name='content_type_place_to_assess')
    place_id = models.PositiveIntegerField()
    place = GenericForeignKey('place_type', 'place_id')

    research_methodology = models.ForeignKey('ResearchMethodology', related_name='places_to_assess')


class ResearchMethodology(models.Model):
    """

    """
    # Relations
    scripts = models.ManyToManyField(QuestionnaireScript)
    questionnaires = models.ManyToManyField(QuestionnaireTemplate)

    # Attributes
    number_of_evaluations = models.PositiveSmallIntegerField()  # or number_of_calls
    description = models.TextField(blank=True)
    # desired_shopper_profile = models.CharField(max_length="1000")

    class Meta:
        verbose_name_plural = 'research methodologies'
        default_related_name = 'research_methodologies'
        ordering = ('number_of_evaluations',)

    def __str__(self):
        return 'Short description: {}, nr. of visits: {}'.format(self.description[0:50], self.number_of_evaluations)

    def prepare_for_update(self):
        self.people_to_assess.all().delete()
        self.places_to_assess.all().delete()
        self.scripts.clear()
        self.questionnaires.clear()


class Project(models.Model):
    """

    """
    # Relations
    tenant = models.ForeignKey(Tenant)
    company = models.ForeignKey(Company)
    # this type of import is used to avoid import circles
    project_manager = models.ForeignKey('users.TenantProjectManager')
    consultants = models.ManyToManyField('users.TenantConsultant')
    shoppers = models.ManyToManyField('users.Shopper')
    research_methodology = models.ForeignKey('ResearchMethodology', null=True, blank=True)

    # Attributes
    period_start = models.DateField()
    period_end = models.DateField()

    class Meta:
        default_related_name = 'projects'
        ordering = ('tenant',)

    def __str__(self):
        return 'Project for {}, start: {}/{}/{}, end: {}/{}/{}'.format(self.company.name,
                                                                       self.period_start.day, self.period_start.month, self.period_start.year%2000,
                                                                       self.period_end.day, self.period_end.month, self.period_start.year%2000)

    def prepare_for_update(self):
        self.project_workers.all().delete()


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
    employee = GenericForeignKey('employee_type', 'employee_id')

    evaluation_choices = Choices((('call', 'Call'),
                                  ('visit', 'Visit')))
    evaluation_type = models.CharField(max_length=6, choices=evaluation_choices)

    suggested_start_date = models.DateTimeField(null=True)
    suggested_end_date = models.DateTimeField(null=True)

    class Meta:
        default_related_name = 'planned_evaluations'

    def __str__(self):
        return '{}, shopper: {}'.format(self.project, self.shopper.user.username)


class AccomplishedEvaluation(TimeStampedModel, PlannedEvaluation):
    """

    """
    # Relations
    questionnaire = models.OneToOneField(Questionnaire)

    # Attributes
    time_accomplished = models.DateTimeField()

    # add timestamp

    class Meta:
        default_related_name = 'accomplished_evaluations'

    def __str__(self):
        return '{}, time accomplished: {}'.format(self.project, str(self.time_accomplished))


class EvaluationAssessmentLevel(models.Model):
    """
    Class used for assessing the review status of a accomplished evaluation
    """
    # Relations
    project = models.ForeignKey(Project)
    previous_level = models.OneToOneField('self', null=True, blank=True, related_name='next_level')
    project_manager = models.ForeignKey('users.TenantProjectManager', null=True)

    # Attributes
    level = models.PositiveIntegerField(null=True, default=0,  blank=True)

    def __str__(self):
        return "Project: {}; level: {}".format(self.project, self.level)
