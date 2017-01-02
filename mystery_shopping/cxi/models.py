from copy import deepcopy

from django.db import models
from model_utils import Choices

from mystery_shopping.questionnaires.models import QuestionnaireQuestion
from mystery_shopping.projects.models import Project
from mystery_shopping.companies.models import Department, CompanyElement
from mystery_shopping.companies.models import Entity
from mystery_shopping.companies.models import Section
from mystery_shopping.tenants.models import Tenant


class CodedCauseLabel(models.Model):
    """
    Model of a Coded Cause name (label) that would allow to use the same name for different Coded Causes
    """
    # Relations
    tenant = models.ForeignKey(Tenant)

    # Attributes
    name = models.CharField(max_length=200)

    def __str__(self):
        return 'Label: {}'.format(self.name)


class WhyCause(models.Model):
    """
    Model for why causes for questions containing the reason why user answered to question
    """
    answer = models.CharField(max_length=400)
    question = models.ForeignKey(QuestionnaireQuestion, related_name='why_causes')
    is_appreciation_cause = models.NullBooleanField()

    def __str__(self):
        return 'Why Cause: {}'.format(self.answer)

    def set_coded_causes(self, coded_causes):
        self.coded_causes.clear()
        self.coded_causes.set(coded_causes)

    def change_appreciation_cause(self):
        self.is_appreciation_cause = not self.is_appreciation_cause
        self.coded_causes.clear()
        self.save()

    def update_answer(self, answer):
        self.answer = answer
        self.save()

    def update_coded_causes(self, coded_causes):
        self.coded_causes.set(coded_causes)

    def create_clones(self, new_answers):
        new_why_causes = list()
        for why_cause_answer in new_answers:
            new_why_cause = deepcopy(self)
            new_why_cause.answer = why_cause_answer
            new_why_cause.pk = None
            new_why_cause.save()

            new_why_cause.coded_causes.set(self.coded_causes.all())

            new_why_causes.append(new_why_cause)

        return new_why_causes


class CodedCause(models.Model):
    """
    Model for Coded Causes that would allow to group different frustration or appreciation together
    """
    # Relations
    tenant = models.ForeignKey(Tenant)
    project = models.ForeignKey(Project)
    coded_label = models.ForeignKey(CodedCauseLabel)
    raw_causes = models.ManyToManyField(WhyCause, related_name='coded_causes', blank=True)
    parent = models.ForeignKey('self', null=True, blank=True)

    # Attributes
    type = models.CharField(max_length=30, blank=True)
    sentiment_choices = Choices(('a', 'Appreciation'),
                                ('f', 'Frustration'))
    sentiment = models.CharField(max_length=1, choices=sentiment_choices, default=sentiment_choices.a)
    WHY_CAUSE_LIMIT = 3

    def __str__(self):
        return '{}, type: {}'.format(self.coded_label.name, self.type)

    def get_few_why_causes(self):
        return self.raw_causes.prefetch_related('coded_causes').all()[:self.WHY_CAUSE_LIMIT]

    def get_number_of_why_causes(self):
        return self.raw_causes.count()


class ProjectComment(models.Model):
    """
    Model for storing comments for a cxi project

    """
    # Relations
    company_element = models.ForeignKey(CompanyElement, null=True, blank=True)
    project = models.ForeignKey(Project)
    # TODO: delete
    department = models.ForeignKey(Department, null=True, blank=True)
    entity = models.ForeignKey(Entity, null=True, blank=True)
    section = models.ForeignKey(Section, null=True, blank=True)
    # till here.

    # Attributes
    causes = models.TextField(blank=True)
    details = models.TextField(blank=True)
    dynamics = models.TextField(blank=True)
    general = models.TextField(blank=True)
    indicator = models.CharField(max_length=30, blank=True)

    class Meta:
        default_related_name = 'project_comments'

    def __str__(self):
        return 'General comment: {}'.format(self.general)
