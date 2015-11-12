from django.db import models

# TODO add description for classes

class Industry(models.Model):
    """

    """
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return 'Name: %s' % self.name


class Company(models.Model):
    """

    """
    # Relations
    industry = models.ForeignKey('Industry')
    country = models.ForeignKey('common.Country')
    tenant = models.ForeignKey('tenants.Tenant')
    # type = models.ForeignKey("CompanyType")

    # Attributes
    name = models.CharField(max_length=50)
    contact_person = models.CharField(max_length=100)
    contact_phone = models.CharField(max_length=20)
    contact_email = models.EmailField(max_length=50)
    domain = models.CharField(verbose_name='the domain of the company on the platform', max_length=30)
    # TODO add MEDIA_ROOT for file upload
    logo = models.ImageField()

    class Meta:
        ordering = ('name',)
        default_related_name = 'companies'

    def __str__(self):
        return 'Name: %s, domain: %s' % (self.name, self.domain)


class Department(models.Model):
    """

    """
    # Relations
    company = models.ForeignKey(Company)
    tenant = models.ForeignKey('tenants.Tenant')

    # Attributes
    name = models.CharField(max_length=255)


    class Meta:
        ordering = ('company', 'name',)
        default_related_name = 'departments'

    def __str__(self):
        return 'Name: %s, company: %s' % (self.name, self.company.name)


class Entity(models.Model):
    """

    """
    # Relations
    department = models.ForeignKey(Department)
    sector = models.ForeignKey('common.Sector', null=True)
    city = models.ForeignKey('common.City')
    tenant = models.ForeignKey('tenants.Tenant')

    # Attributes
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    coordinates = models.CharField(max_length=50)

    class Meta:
        ordering = ('department', 'name',)
        default_related_name = 'entities'

    def __str__(self):
        return 'Name: %s, department: %s' % (self.name, self.department.name)


class Section(models.Model):
    """

    """
    # Relations
    entity = models.ForeignKey(Entity)
    tenant = models.ForeignKey('tenants.Tenant')

    # Attributes
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ('entity', 'name',)
        default_related_name = 'sections'

    def __str__(self):
        return 'Name: %s, entity: %s' % (self.name, self.entity.name)
