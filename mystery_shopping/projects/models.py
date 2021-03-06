from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.deletion import PROTECT, SET_NULL
from model_utils import Choices
from model_utils.fields import StatusField
from model_utils.models import TimeStampedModel

from mystery_shopping.companies.models import CompanyElement
from mystery_shopping.mystery_shopping_utils.models import TenantModel
from mystery_shopping.projects.constants import (EvaluationStatus,
                                                 RespondentType)
from mystery_shopping.projects.managers import (EvaluationQuerySet,
                                                ProjectQuerySet)
from mystery_shopping.questionnaires.models import (Questionnaire,
                                                    QuestionnaireQuestion,
                                                    QuestionnaireScript,
                                                    QuestionnaireTemplate)
from mystery_shopping.tenants.models import Tenant


class ResearchMethodology(TenantModel):
    """

    """
    # Relations
    company_elements = models.ManyToManyField('companies.CompanyElement')
    questionnaires = models.ManyToManyField(QuestionnaireTemplate)
    scripts = models.ManyToManyField(QuestionnaireScript)

    # Attributes
    description = models.TextField(blank=True)
    number_of_evaluations = models.PositiveIntegerField()  # or number_of_calls

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
    consultants = models.ManyToManyField('users.User', blank=True, related_name='consultant_projects')
    company = models.ForeignKey('companies.CompanyElement')
    project_manager = models.ForeignKey('users.User', related_name='manager_projects', on_delete=PROTECT)
    detractors_manager = models.ForeignKey('users.User', null=True, blank=True,
                                           related_name='detractors_manager_projects', on_delete=PROTECT)
    research_methodology = models.ForeignKey('ResearchMethodology', null=True, blank=True, on_delete=SET_NULL)
    shoppers = models.ManyToManyField('users.User', blank=True, related_name='shopper_projects')

    # Attributes
    name = models.CharField(max_length=150)
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
        return '{}, id:{}'.format(self.name, self.pk)

    def get_indicators_list(self):
        from mystery_shopping.cxi.algorithms import get_project_indicator_questions_list
        return get_project_indicator_questions_list(self)

    def get_company_elements_with_evaluations(self):
        """
        Method for getting all company elements that are included into the current project
        and have at least an evaluation in the project and cannot be removed from the research methodology
        :return: A list of company elements' ids
        """
        editable_places = []
        if self.research_methodology:
            editable_places = CompanyElement.objects.get_list_of_non_editable_places(project=self)
        return editable_places

    def get_company_elements_not_in_project(self):
        """
        Method for getting all company elements in the company that aren't part of the project's
        research methodology
        :return: A list of company elements' ids
        """
        not_in_project_company_elements = []
        if self.research_methodology:
            not_in_project_company_elements = CompanyElement.objects.get_company_elements_not_in_project(project=self)
        return not_in_project_company_elements

    def get_company_elements_in_project(self):
        return self.research_methodology.company_elements.all()

    def is_questionnaire_editable(self):
        """
        Method for checking if a questionnaire is editable and
        there exists evaluations that include this questionnaire
        :return: Boolean
        """
        if self.research_methodology:
            return not self.research_methodology.get_questionnaires().filter(evaluation__project=self).exists()
        else:
            return True

    def get_total_number_of_evaluations(self):
        return self.research_methodology.number_of_evaluations


class Evaluation(TimeStampedModel, models.Model):
    """
    """
    # Relationships
    company_element = models.ForeignKey('companies.CompanyElement', on_delete=PROTECT)
    project = models.ForeignKey(Project)
    questionnaire_script = models.ForeignKey(QuestionnaireScript, null=True)
    saved_by_user = models.ForeignKey('users.User', related_name='saved_evaluations')
    shopper = models.ForeignKey('users.User', null=True)

    # For "Accomplished"
    questionnaire_template = models.ForeignKey(QuestionnaireTemplate)
    questionnaire = models.OneToOneField(Questionnaire, null=True, blank=True, related_name='evaluation')
    evaluation_assessment_level = models.ForeignKey('EvaluationAssessmentLevel', null=True, blank=True)

    # Attributes
    evaluation_choices = Choices(('call', 'Call'),
                                 ('visit', 'Visit'))
    evaluation_type = StatusField(choices_name='evaluation_choices')
    is_draft = models.BooleanField(default=True)

    suggested_start_date = models.DateTimeField(null=True)
    suggested_end_date = models.DateTimeField(null=True)
    time_accomplished = models.DateTimeField(null=True, blank=True)

    visit_time = models.DateTimeField(null=True)

    STATUS = Choices((EvaluationStatus.PLANNED, 'Planned'),
                     (EvaluationStatus.DRAFT, 'Draft'),
                     (EvaluationStatus.SUBMITTED, 'Submitted'),
                     (EvaluationStatus.REVIEWED, 'Reviewed'),
                     (EvaluationStatus.APPROVED, 'Approved'),
                     (EvaluationStatus.DECLINED, 'Declined'),
                     (EvaluationStatus.REJECTED, 'Rejected'))
    status = StatusField()

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

    def get_indicator_questions(self):
        return self.questionnaire.get_indicator_questions()

    def get_detractor_questions(self):
        return self.questionnaire.get_indicator_questions().filter(score__lte=RespondentType.DETRACTOR_HIGH.value)

    def number_of_detractor_questions(self):
        return self.get_detractor_questions().count()

    def get_detractors_manager(self):
        return self.project.detractors_manager

    def get_company(self):
        return self.project.company


class EvaluationAssessmentLevel(models.Model):
    """
    Class used for assessing the review status of a accomplished evaluation
    """
    # Relations
    project = models.ForeignKey(Project)
    previous_level = models.OneToOneField('self', null=True, blank=True, related_name='next_level')
    users = models.ManyToManyField('users.User', blank=True)

    # Attributes
    level = models.PositiveIntegerField(null=True, default=0, blank=True)

    class Meta:
        ordering = ('level',)
        default_related_name = 'evaluation_assessment_levels'

    def __str__(self):
        return 'Project: {}; level: {}'.format(self.project, self.level)


class EvaluationAssessmentComment(models.Model):
    """

    """
    # Relations
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
        return 'Comment: {}, consultant: {}'.format(self.comment[:50], self.commenter)
