from django.contrib.postgres.fields.jsonb import JSONField
from django.db import models
from mptt.fields import TreeForeignKey
from mptt.managers import TreeManager
from mptt.models import MPTTModel

from mystery_shopping.companies.managers import CompanyElementQuerySet
from mystery_shopping.mystery_shopping_utils.models import TenantModel


class CompanyElement(TenantModel, MPTTModel):
    """
    A generic company element.
    It may be the company itself, a section, department, employee, etc.
    """
    # Relations
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)

    # Attributes
    additional_info = JSONField(null=True, blank=True)
    element_name = models.CharField(max_length=100)
    element_type = models.CharField(max_length=100)
    order = models.SmallIntegerField(null=True, blank=True)
    logo = models.ImageField(null=True, blank=True)

    tree = TreeManager()
    objects = models.Manager.from_queryset(CompanyElementQuerySet)()

    class Meta:
        default_related_name = 'company_elements'
        permissions = (
            ('manager_companyelement', 'Manager of company element'),
            ('view_detractors_for_companyelement', 'View detractors for company element'),
            ('view_statistics_for_companyelement', 'View statistics for company element'),
            ('view_coded_causes_for_companyelement', 'View detractors for company element'),
        )

    def __str__(self):
        return 'company_element: {id: %s, name: %s, type: %s}' % (self.pk, self.element_name, self.element_type)

    def update_order(self, new_order):
        self.order = new_order
        self.save(update_fields=['order'])

    def update_parent(self, new_parent):
        self.parent = new_parent
        self.save(update_fields=['parent'])


class AdditionalInfoType(TenantModel):
    """
    A saved additional info type for Company Element 'additional_info' attribute
    """
    # Attributes
    name = models.CharField(max_length=100)
    input_type = models.CharField(max_length=50)
    icon = models.CharField(max_length=50)

    def __str__(self):
        return 'additional_info_type: {id: %s, name: %s}' % (self.pk, self.name)


class Industry(models.Model):
    """

    """
    # Attributes
    name = models.CharField(max_length=200)

    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'industries'

    def __str__(self):
        return 'Name: %s' % self.name


class SubIndustry(models.Model):
    """

    """
    # Attributes
    name = models.CharField(max_length=200)
    industry = models.ForeignKey(Industry, related_name='subindustry')

    class Meta:
        verbose_name_plural = 'sub-industries'

    def __str__(self):
        return 'Name: %s' % self.name

    def return_industry_and_subindustry(self):
        return '{}: {}'.format(self.industry.name, self.name)
