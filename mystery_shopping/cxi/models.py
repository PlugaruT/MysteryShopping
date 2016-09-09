from django.db import models
from model_utils import Choices

from mystery_shopping.questionnaires.models import QuestionnaireQuestion
from mystery_shopping.projects.models import Project
from mystery_shopping.projects.models import Entity
from mystery_shopping.tenants.models import Tenant


class CodedCauseLabel(models.Model):
    """
    Model of a Coded Cause name (label) that would allow to use the same name for different Coded Causes
    """
    # Relations
    tenant = models.ForeignKey(Tenant)

    # Attributes
    name = models.CharField(max_length=50)

    def __str__(self):
        return 'Label: {}'.format(self.name)


class WhyCause(models.Model):
    """
    Model for why causes for questions containing the reason why user answered to question
    """
    answer = models.CharField(max_length=100)
    question = models.ForeignKey(QuestionnaireQuestion, related_name='why_causes')
    is_appreciation_cause = models.NullBooleanField()

    def __str__(self):
        return 'Why Cause: {}'.format(self.answer)

    def set_coded_causes(self, coded_causes):
        self.coded_causes.clear()
        self.coded_causes.set(coded_causes)


class CodedCause(models.Model):
    """
    Model for Coded Causes that would allow to group different frustration or appreciation together
    """
    # Relations
    tenant = models.ForeignKey(Tenant)
    coded_label = models.ForeignKey(CodedCauseLabel)
    raw_causes = models.ManyToManyField(WhyCause, related_name='coded_causes', blank=True)
    parent = models.ForeignKey('self', null=True, blank=True)

    # Attributes
    type = models.CharField(max_length=30, blank=True)

    sentiment_choices = Choices(('a', 'Appreciation'),
                                ('f', 'Frustration'))
    sentiment = models.CharField(max_length=1, choices=sentiment_choices, default=sentiment_choices.a)

    def __str__(self):
        return '{}, type: {}'.format(self.coded_label.name, self.type)


class ProjectComment(models.Model):
    """
    Model for storing comments for a cxi project

    """
    # Relations
    project = models.ForeignKey(Project)
    entity = models.ForeignKey(Entity, null=True, blank=True)

    # Attributes
    indicator = models.CharField(max_length=30, blank=True)
    general = models.TextField(blank=True)
    dynamics = models.TextField(blank=True)
    details = models.TextField(blank=True)
    causes = models.TextField(blank=True)

    class Meta:
        default_related_name = 'project_comments'

    def __str__(self):
        return 'General comment: {}'.format(self.general)
