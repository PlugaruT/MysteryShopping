from django.db import models
# from django.contrib.postgres.fields import

from mystery_shopping.tenants.models import Tenant



class DashboardTemplate(models.Model):
    """
    Model for storing the user defined dashboard structure
    """
    # Relations
    tenant = models.ForeignKey(Tenant)

    # Attributes
    structure = models.TextField()


class DashboardComment(models.Model):
    """
    Model that will be displayed in a dashboard card
    """
    # Relations
    dashboard = models.ForeignKey(DashboardTemplate)

    # Attributes
    title = models.CharField(max_length=30, null=True, blank=True)
    comment = models.TextField()




