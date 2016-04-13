from django.db import models


class Tenant(models.Model):
    """

    """
    # Attributes
    name = models.CharField(max_length=60)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return 'Name: %s' % self.name