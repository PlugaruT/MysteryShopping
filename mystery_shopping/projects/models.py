from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from model_utils import Choices
from model_utils.models import TimeStampedModel
from model_utils.fields import StatusField

from mystery_shopping.companies.models import Company, Department, Entity, Section
from mystery_shopping.projects.managers import ProjectQuerySet
from mystery_shopping.questionnaires.models import QuestionnaireScript, QuestionnaireTemplate
from mystery_shopping.tenants.models import Tenant
from mystery_shopping.questionnaires.models import QuestionnaireTemplate
from mystery_shopping.questionnaires.models import Questionnaire
from mystery_shopping.projects.constants import ProjectStatus
from mystery_shopping.questionnaires.constants import IndicatorQuestionType


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
    tenant = models.ForeignKey(Tenant)
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
    type_questionnaire = Choices(('m', 'Mystery Questionnaire'),
                                 ('c', 'Customer Experience Index Questionnaire'))
    type = models.CharField(max_length=1, choices=type_questionnaire, default=type_questionnaire.m)

    objects = models.Manager.from_queryset(ProjectQuerySet)()

    class Meta:
        default_related_name = 'projects'
        ordering = ('tenant',)

    def __str__(self):
        return 'Project for {}, start: {}/{}/{}, end: {}/{}/{}'.format(self.company.name,
                                                                       self.period_start.day, self.period_start.month, self.period_start.year%2000,
                                                                       self.period_end.day, self.period_end.month, self.period_start.year%2000)

    def get_indicators_list(self):
        # get the template questionnaire for this project
        indicator_set = set()
        if self.research_methodology:
            template_questionnaire = self.research_methodology.questionnaires.first()
            for question in template_questionnaire.template_questions.all():
                if question.type == IndicatorQuestionType.INDICATOR_QUESTION:
                    indicator_set.add(question.additional_info)
        return indicator_set



class Evaluation(TimeStampedModel, models.Model):
    """
    """
    # Relationships
    project = models.ForeignKey(Project)
    shopper = models.ForeignKey('users.Shopper')
    questionnaire_script = models.ForeignKey(QuestionnaireScript, null=True)

    type_questionnaire = Choices(('m', 'Mystery Evaluation'),
                                 ('c', 'Customer Experience Index Evaluation'))
    type = models.CharField(max_length=1, choices=type_questionnaire, default=type_questionnaire.m)

    questionnaire_template = models.ForeignKey(QuestionnaireTemplate)
    entity = models.ForeignKey(Entity)
    section = models.ForeignKey(Section, null=True, blank=True)

    limit = models.Q(app_label='users', model='clientmanager') | \
            models.Q(app_label='users', model='clientemployee')
    employee_type = models.ForeignKey(ContentType, limit_choices_to=limit, related_name='employee_type', null=True, blank=True)
    employee_id = models.PositiveIntegerField(null=True, blank=True)
    employee = GenericForeignKey('employee_type', 'employee_id')

    # For "Accomplished"
    questionnaire = models.OneToOneField(Questionnaire, null=True, blank=True, related_name='evaluation')
    evaluation_assessment_level = models.ForeignKey('EvaluationAssessmentLevel', null=True, blank=True)

    # Attributes
    evaluation_choices = Choices(('call', 'Call'),
                                 ('visit', 'Visit'))
    evaluation_type = StatusField(choices_name='evaluation_choices')
    is_draft = models.BooleanField(default=True)

    suggested_start_date = models.DateTimeField(null=True)
    suggested_end_date = models.DateTimeField(null=True)

    STATUS = Choices((ProjectStatus.PLANNED, 'Planned'),
                     (ProjectStatus.DRAFT, 'Draft'),
                     (ProjectStatus.SUBMITTED, 'Submitted'),
                     (ProjectStatus.REVIEWED, 'Reviewed'),
                     (ProjectStatus.APPROVED, 'Approved'),
                     (ProjectStatus.DECLINED, 'Declined'),
                     (ProjectStatus.REJECTED, 'Rejected'))
    status = StatusField()
    # For "Accomplished"
    time_accomplished = models.DateTimeField(null=True, blank=True)

    class Meta:
        default_related_name = 'evaluations'

    def __str__(self):
        if self.time_accomplished is not None:
            return '{}, shopper: {}'.format(self.project, self.shopper.user.username)
        else:
            return '{}, time accomplished: {}'.format(self.project, str(self.time_accomplished))

    def save(self, *args, **kwargs):
        if self.status == ProjectStatus.SUBMITTED:
            self.questionnaire_template.is_editable = False
            self.questionnaire_template.save()

            # In case there is no evaluation assessment level defined for the
            # submitted evaluation, assign the first level to it.
            if self.evaluation_assessment_level is None:
                first_evaluation_assessment_level = EvaluationAssessmentLevel.objects \
                    .filter(project=self.project, previous_level__isnull=True) \
                    .first()

                # In case there exist an evaluation level, assign it
                if first_evaluation_assessment_level is not None:
                    self.evaluation_assessment_level = first_evaluation_assessment_level

                # Otherwise, this means there are no evaluation assessment levels
                # defined for this project, thus assign the `approved` status
                # for the submitted evaluation.
                else:
                    self.status = ProjectStatus.APPROVED

        super(Evaluation, self).save(*args, **kwargs)


class EvaluationAssessmentLevel(models.Model):
    """
    Class used for assessing the review status of a accomplished evaluation
    """
    # Relations
    project = models.ForeignKey(Project)
    previous_level = models.OneToOneField('self', null=True, blank=True, related_name='next_level')
    project_manager = models.ForeignKey('users.TenantProjectManager', null=True)
    consultants = models.ManyToManyField('users.TenantConsultant')

    # Attributes
    level = models.PositiveIntegerField(null=True, default=0,  blank=True)

    class Meta:
        ordering = ('level',)
        default_related_name = 'evaluation_assessment_levels'

    def __str__(self):
        return "Project: {}; level: {}".format(self.project, self.level)


class EvaluationAssessmentComment(models.Model):
    """

    """
    # Relations
    limit = models.Q(app_label='users', model='tenantprojectmanager') | \
            models.Q(app_label='users', model='tenantconsultant')
    commenter_type = models.ForeignKey(ContentType, limit_choices_to=limit, related_name='commenter_type')
    commenter_id = models.PositiveIntegerField()
    commenter = GenericForeignKey('commenter_type', 'commenter_id')
    evaluation_assessment_level = models.ForeignKey(EvaluationAssessmentLevel)
    evaluation = models.ForeignKey(Evaluation)
    questionnaire = models.ForeignKey(Questionnaire)

    # Attributes
    comment = models.TextField()

    class Meta:
        default_related_name = 'evaluation_assessment_comments'

    def __str__(self):
        return "Comment: {}, consultant: {}".format(self.comment[:50], self.commenter)
