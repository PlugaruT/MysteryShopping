from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models.query_utils import Q
from model_utils import Choices
from model_utils.models import TimeStampedModel
from model_utils.fields import StatusField

from mystery_shopping.companies.models import Department, Entity, Section
from mystery_shopping.mystery_shopping_utils.models import TenantModel
from mystery_shopping.projects.managers import ProjectQuerySet, EvaluationQuerySet
from mystery_shopping.questionnaires.models import QuestionnaireScript, QuestionnaireTemplate
from mystery_shopping.tenants.models import Tenant
from mystery_shopping.questionnaires.models import QuestionnaireTemplate
from mystery_shopping.questionnaires.models import Questionnaire
from mystery_shopping.questionnaires.models import QuestionnaireQuestion
from mystery_shopping.projects.constants import EvaluationStatus


# TODO: Delete model
class PlaceToAssess(models.Model):
    """
    A class with a generic foreign key for setting places to be evaluated for a project.

    A person to assess can either be an Entity or a Section
    """
    limit = models.Q(app_label='companies', model='department') |\
            models.Q(app_label='companies', model='entity') |\
            models.Q(app_label='companies', model='section')
    place_type = models.ForeignKey(ContentType, limit_choices_to=limit, related_name='content_type_place_to_assess')
    place_id = models.PositiveIntegerField()
    place = GenericForeignKey('place_type', 'place_id')

    research_methodology = models.ForeignKey('ResearchMethodology', related_name='places_to_assess')

    def evaluations(self):
        return self.place.evaluations


class ResearchMethodology(TenantModel):
    """

    """
    # Relations
    company_elements = models.ManyToManyField('companies.CompanyElement')
    questionnaires = models.ManyToManyField(QuestionnaireTemplate)
    scripts = models.ManyToManyField(QuestionnaireScript)

    # Attributes
    description = models.TextField(blank=True)
    number_of_evaluations = models.PositiveSmallIntegerField()  # or number_of_calls

    class Meta:
        verbose_name_plural = 'research methodologies'
        default_related_name = 'research_methodologies'
        ordering = ('number_of_evaluations',)

    def __str__(self):
        return 'Short description: {}, nr. of visits: {}'.format(self.description[0:50], self.number_of_evaluations)

    def get_questionnaires(self):
        # and the award for the most legible code gooooooes to:
        return self.questionnaires.first().questionnaires


class Project(TenantModel):
    """

    """
    # Relations
    # this type of import is used to avoid import circles
    consultants_new = models.ManyToManyField('users.User', related_name='consultant_projects')
    consultants = models.ManyToManyField('users.TenantConsultant')
    # TODO rename to 'company'
    company_new = models.ForeignKey('companies.CompanyElement')
    # TODO delete
    company = models.ForeignKey('companies.Company')
    project_manager_new = models.ForeignKey('users.User', related_name='manager_projects')
    project_manager = models.ForeignKey('users.TenantProjectManager')
    research_methodology = models.ForeignKey('ResearchMethodology', null=True, blank=True)
    # Todo (remove)
    shoppers_new = models.ManyToManyField('users.User', blank=True, related_name='shopper_projects')
    shoppers = models.ManyToManyField('users.Shopper', blank=True)

    # Attributes
    # Todo: (delete)
    graph_config = JSONField(null=True)
    type_questionnaire = Choices(('m', 'Mystery Questionnaire'),
                                 ('c', 'Customer Experience Index Questionnaire'))
    type = models.CharField(max_length=1, choices=type_questionnaire, default=type_questionnaire.m)
    period_start = models.DateField()
    period_end = models.DateField()

    objects = models.Manager.from_queryset(ProjectQuerySet)()

    class Meta:
        default_related_name = 'projects'
        ordering = ('tenant',)

    def __str__(self):
        return 'Project for {}, start: {}/{}/{}, end: {}/{}/{}'.format(self.company.name,
                                                                       self.period_start.day, self.period_start.month, self.period_start.year%2000,
                                                                       self.period_end.day, self.period_end.month, self.period_start.year%2000)

    def get_indicators_list(self):
        from mystery_shopping.cxi.algorithms import get_project_indicator_questions_list
        return get_project_indicator_questions_list(self)

    # Todo: rewrite or delete
    def get_editable_places(self):
        """
        Function for getting all entities and sections that aren't included into any project and
        doesn't have a questionnaire and can be removed from project
        :return: A list of dicts with information about each place to asses
        """
        editable_places = []
        if self.research_methodology:
            places_to_asses = self.research_methodology.places_to_assess.filter(~Q(place_type=ContentType.objects.get_for_model(Department)))

            for place_to_asses in places_to_asses:
                if not place_to_asses.evaluations().filter(project=self).exists():
                    place_info = {
                        'place_type': place_to_asses.place_type_id,
                        'place_id': place_to_asses.place_id
                    }
                    editable_places.append(place_info)
        return editable_places

    def is_questionnaire_editable(self):
        """
        Function for checking if a questionnaire is editable and
        there exists evaluations that include this questionnaire
        :return: Boolean
        """
        if self.research_methodology:
            return not self.research_methodology.get_questionnaires().filter(evaluation__project=self).exists()
        else:
            return True

    # Todo: decide if this belongs here
    def save_graph_config(self, config):
        self.graph_config = config
        self.save()

    def get_total_number_of_evaluations(self):
        return self.research_methodology.number_of_evaluations


class Evaluation(TimeStampedModel, models.Model):
    """
    """
    # Relationships
    company_element = models.ForeignKey('companies.CompanyElement')
    project = models.ForeignKey(Project)
    questionnaire_script = models.ForeignKey(QuestionnaireScript, null=True)
    saved_by_user = models.ForeignKey('users.User', related_name='saved_evaluations')
    # collector? FK to User
    shopper_new = models.ForeignKey('users.User', null=True)
    shopper = models.ForeignKey('users.Shopper', null=True)

    #  TODO: Remove from here
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
    # till here

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

    visit_time = models.DateTimeField(null=True)

    STATUS = Choices((EvaluationStatus.PLANNED, 'Planned'),
                     (EvaluationStatus.DRAFT, 'Draft'),
                     (EvaluationStatus.SUBMITTED, 'Submitted'),
                     (EvaluationStatus.REVIEWED, 'Reviewed'),
                     (EvaluationStatus.APPROVED, 'Approved'),
                     (EvaluationStatus.DECLINED, 'Declined'),
                     (EvaluationStatus.REJECTED, 'Rejected'))
    status = StatusField()
    # For "Accomplished"
    time_accomplished = models.DateTimeField(null=True, blank=True)

    objects = models.Manager.from_queryset(EvaluationQuerySet)()

    class Meta:
        default_related_name = 'evaluations'

    def __str__(self):
        if self.time_accomplished is not None:
            return '{}, shopper: {}'.format(self.project, self.saved_by_user.username)
        else:
            return '{}, time accomplished: {}'.format(self.project, str(self.time_accomplished))

    def save(self, *args, **kwargs):
        if self.status == EvaluationStatus.SUBMITTED:
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
                    self.status = EvaluationStatus.APPROVED

        super(Evaluation, self).save(*args, **kwargs)


class EvaluationAssessmentLevel(models.Model):
    """
    Class used for assessing the review status of a accomplished evaluation
    """
    # Relations
    project = models.ForeignKey(Project)
    previous_level = models.OneToOneField('self', null=True, blank=True, related_name='next_level')
    users = models.ManyToManyField('users.User', blank=True)
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
    user = models.ForeignKey('users.User')
    evaluation_assessment_level = models.ForeignKey(EvaluationAssessmentLevel)
    evaluation = models.ForeignKey(Evaluation)
    questionnaire = models.ForeignKey(Questionnaire)
    question = models.ForeignKey(QuestionnaireQuestion, null=True)

    # Attributes
    comment = models.TextField()

    class Meta:
        default_related_name = 'evaluation_assessment_comments'

    def __str__(self):
        return "Comment: {}, consultant: {}".format(self.comment[:50], self.commenter)
