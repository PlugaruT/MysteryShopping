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

    def __str__(self):
        return 'Dashboard for {}'.format(self.tenant.name)


class DashboardComment(models.Model):
    """
    Model that will be displayed in a dashboard card
    """
    # Relations
    dashboard = models.ForeignKey(DashboardTemplate, related_name='dashboard_comments')

    # Attributes
    title = models.CharField(max_length=30, null=True, blank=True)
    comment = models.TextField()

    def __str__(self):
        return 'Dashboard Comment: {}'.format(self.title)
