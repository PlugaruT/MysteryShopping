from django.db import models
from model_utils import Choices

from mystery_shopping.questionnaires.models import QuestionnaireQuestion
from mystery_shopping.tenants.models import Tenant

class CodedCauseLabel(models.Model):
    """
    Model of a Coded Cause name (label) that would allow to use the same name for different Coded Causes
    """
    # Relations
    tenant = models.ForeignKey(Tenant)

    # Attributes
    name = models.CharField(max_length=50)


class CodedCause(models.Model):
    """
    Model for Coded Causes that would allow to group different frustration or appreciation together
    """
    # Relations
    tenant = models.ForeignKey(Tenant)
    coded_label = models.ForeignKey(CodedCauseLabel)
    raw_causes = models.ManyToManyField(QuestionnaireQuestion, related_name='coded_causes')
    parent = models.ForeignKey('self', null=True, blank=True)

    # Attributes
    type_choices = Choices('n', 'NPS questions',
                           'j', 'Enjoyability questions',
                           'e', 'Easiness questions',
                           'u', 'Usefulness questions')
    type = models.CharField(max_length=1, choices=type_choices, default=type_choices.n)
