from django.db import models

from mystery_shopping.companies.models import Company, Department, Entity, Section
from mystery_shopping.questionnaires.models import QuestionnaireScript, QuestionnaireTemplate
from mystery_shopping.tenants.models import Tenant


class ResearchMethodology(models.Model):
    """

    """
    # Relations
    scripts = models.ForeignKey(QuestionnaireScript)
    questionnaires = models.ForeignKey(QuestionnaireTemplate)

    # Attributes
    number_of_visits = models.PositiveSmallIntegerField()  # or number_of_calls
    # desired_shopper_profile = models.CharField(max_length="1000")

    class Meta:
        verbose_name_plural = 'research methodologies'
        default_related_name = 'research_methodologies'
        ordering = ('questionnaires',)


class Project(models.Model):
    """

    """
    # Relations
    tenant = models.ForeignKey(Tenant)
    client = models.ForeignKey(Company)
    departments = models.ForeignKey(Department, null=True)
    entities = models.ForeignKey(Entity, null=True)
    sections = models.ForeignKey(Section, null=True)
    # employees = models.ForeignKey(Employee, null=True)
    # shoppers = models.ForeignKey(Shopper, null=True)
    research_methodology = models.ForeignKey(ResearchMethodology)

    # Attributes
    period_start = models.DateField()
    period_end = models.DateField()

    class Meta:
        default_related_name = 'projects'
        ordering = ('tenant',)

