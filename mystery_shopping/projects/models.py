from django.db import models

from mystery_shopping.companies.models import Company, Department, Entity, Section
from mystery_shopping.questionnaires.models import QuestionnaireScript, QuestionnaireTemplate
from mystery_shopping.tenants.models import Tenant


class Project(models.Model):
    """

    """
    # Relations
    tenant = models.ForeignKey(Tenant)
    client = models.ForeignKey(Company)
    # shoppers = models.ForeignKey(Shopper, null=True)

    # Attributes
    period_start = models.DateField()
    period_end = models.DateField()

    class Meta:
        default_related_name = 'projects'
        ordering = ('tenant',)


class ResearchMethodology(models.Model):
    """

    """
    # Relations
    # many to many fields
    scripts = models.ForeignKey(QuestionnaireScript)
    questionnaires = models.ForeignKey(QuestionnaireTemplate)
    # TODO: add list of places
    # TODO: add list of people
    research_methodology = models.ForeignKey(Project)

    # Attributes
    number_of_evaluations = models.PositiveSmallIntegerField()  # or number_of_calls
    description = models.TextField(blank=True)
    # desired_shopper_profile = models.CharField(max_length="1000")

    class Meta:
        verbose_name_plural = 'research methodologies'
        default_related_name = 'research_methodologies'
        ordering = ('questionnaires',)

