from django.db import models
from django.contrib.contenttypes.fields import GenericRelation

from mystery_shopping.common.models import City, Country, Sector
from mystery_shopping.tenants.models import Tenant

# TODO add description for classes


class HasEvaluationsMixin:
    @staticmethod
    def check_for_evaluations(subdivisions):
        return any((subdivision.has_evaluations() for subdivision in subdivisions))

    def at_least_one_manager_has_evaluations(self):
        return self.check_for_evaluations(self.managers.all())

    def at_least_one_employee_has_evaluations(self):
        return self.check_for_evaluations(self.employees.all())

    def at_least_one_section_has_evaluations(self):
        return self.check_for_evaluations(self.sections.all())


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


class Company(models.Model):
    """

    """
    # Relations
    industry = models.ForeignKey(Industry)
    country = models.ForeignKey(Country)
    tenant = models.ForeignKey(Tenant)

    # Attributes
    name = models.CharField(max_length=50)
    contact_person = models.CharField(max_length=100)
    contact_phone = models.CharField(max_length=20)
    contact_email = models.EmailField(max_length=50)
    contact_position = models.CharField(max_length=100, blank=True)
    domain = models.CharField(verbose_name='the domain of the company on the platform', max_length=30)
    logo = models.ImageField(null=True, blank=True)

    class Meta:
        ordering = ('name',)
        default_related_name = 'companies'
        verbose_name_plural = 'companies'

    def __str__(self):
        return 'Name: %s, domain: %s' % (self.name, self.domain)


class Department(HasEvaluationsMixin, models.Model):
    """

    """
    # Relations
    company = models.ForeignKey(Company)
    tenant = models.ForeignKey(Tenant)
    managers = GenericRelation('users.ClientManager',
                               content_type_field='place_type',
                               object_id_field='place_id')

    # Attributes
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ('company', 'name',)
        default_related_name = 'departments'

    def __str__(self):
        return 'Name: %s, company: %s' % (self.name, self.company.name)

    def has_evaluations(self):
        return self.at_least_one_entity_has_evaluations() or self.at_least_one_manager_has_evaluations()


# PoS
class Entity(HasEvaluationsMixin, models.Model):
    """

    """
    # Relations
    department = models.ForeignKey(Department)
    sector = models.ForeignKey(Sector, null=True)
    city = models.ForeignKey(City)
    tenant = models.ForeignKey(Tenant)
    managers = GenericRelation('users.ClientManager',
                               content_type_field='place_type',
                               object_id_field='place_id')

    # Attributes
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    coordinates = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        ordering = ('department', 'name',)
        default_related_name = 'entities'
        verbose_name_plural = 'entities'

    def __str__(self):
        return 'Name: %s, department: %s' % (self.name, self.department.name)

    def has_evaluations(self):
        return self.at_least_one_manager_has_evaluations() or self.at_least_one_employee_has_evaluations() or \
               self.at_least_one_section_has_evaluations() or self.entity_has_at_least_one_evaluation()

    def entity_has_at_least_one_evaluation(self):
        return self.evaluations.exists()


class Section(HasEvaluationsMixin, models.Model):
    """

    """
    # Relations
    entity = models.ForeignKey(Entity)
    tenant = models.ForeignKey(Tenant)
    managers = GenericRelation('users.ClientManager',
                               content_type_field='place_type',
                               object_id_field='place_id')

    # Attributes
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ('entity', 'name',)
        default_related_name = 'sections'

    def __str__(self):
        return 'Name: %s, entity: %s' % (self.name, self.entity.name)

    def has_evaluations(self):
        return self.at_least_one_manager_has_evaluations() or self.at_least_one_employee_has_evaluations or \
               self.section_has_at_least_one_evaluation()

    def section_has_at_least_one_evaluation(self):
        return self.evaluations.exists()
