from django.db import models
from django.contrib.contenttypes.fields import GenericRelation

from mystery_shopping.common.models import City, Country, Sector
from mystery_shopping.tenants.models import Tenant

# TODO add description for classes


class Industry(models.Model):
    """

    """
    # Attributes
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'industries'

    def __str__(self):
        return 'Name: %s' % self.name


class SubIndustry(models.Model):
    """

    """
    # Attributes
    name = models.CharField(max_length=100)
    industry = models.ForeignKey(Industry)

    class Meta:
        verbose_name_plural = 'sub-industries'

    def __str__(self):
        return 'Name: %s' % self.name


class Company(models.Model):
    """

    """
    # Relations
    industry = models.ForeignKey(Industry)
    country = models.ForeignKey(Country)
    tenant = models.ForeignKey(Tenant)
    # type = models.ForeignKey("CompanyType")

    # Attributes
    name = models.CharField(max_length=50)
    contact_person = models.CharField(max_length=100)
    contact_phone = models.CharField(max_length=20)
    contact_email = models.EmailField(max_length=50)
    domain = models.CharField(verbose_name='the domain of the company on the platform', max_length=30)
    logo = models.ImageField(null=True, blank=True)

    class Meta:
        ordering = ('name',)
        default_related_name = 'companies'
        verbose_name_plural = 'companies'

    def __str__(self):
        return 'Name: %s, domain: %s' % (self.name, self.domain)


class Department(models.Model):
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


# PoS
class Entity(models.Model):
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


class Section(models.Model):
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
