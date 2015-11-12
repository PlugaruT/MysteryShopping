from django.db import models


class Country(models.Model):
    """

    """
    # Attributes
    name = models.CharField(max_length=30)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return 'Name: %s' % self.name


class CountryRegion(models.Model):
    """

    """
    # Attributes
    name = models.CharField(max_length=50)

    class Meta:
        ordering = ('name',)
        default_related_name = 'regions'

    def __str__(self):
        return 'Name: %s' % self.name


class County(models.Model):
    """

    """
    # Relations
    country_region = models.ForeignKey(CountryRegion)
    country = models.ForeignKey(Country)

    # Attributes
    name = models.CharField(max_length=50)

    class Meta:
        ordering = ('name',)
        default_related_name = 'counties'

    def __str__(self):
        return 'Name: %s' % self.name


class City(models.Model):
    """

    """
    # Relations
    county = models.ForeignKey(County)

    # Attributes
    name = models.CharField(max_length=40)

    class Meta:
        ordering = ('county', 'name',)
        default_related_name = 'cities'

    def __str__(self):
        return 'Name: %s, County: %s' % (self.name, self.county.name)


class Sector(models.Model):
    """

    """
    # Relations
    city = models.ForeignKey(City)

    # Attributes
    name = models.CharField(max_length=40)

    class Meta:
        ordering = ('city', 'name',)
        default_related_name = 'sectors'

    def __str__(self):
        return 'Name: %s, City: %s' % (self.name, self.city.name)
