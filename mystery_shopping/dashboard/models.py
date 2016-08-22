from django.db import models

from mystery_shopping.companies.models import Company
from mystery_shopping.tenants.models import Tenant
from mystery_shopping.projects.models import Project
from mystery_shopping.users.models import User
from datetime import datetime


class DashboardTemplate(models.Model):
    """
    Model for storing the user defined dashboard structure
    """
    # Relations
    tenant = models.ForeignKey(Tenant)
    company = models.ForeignKey(Company)
    modified_by = models.ForeignKey(User)

    # Attributes
    title = models.CharField(max_length=120)
    widgets = models.TextField()
    is_published = models.BooleanField(default=False)
    modified_date = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return 'Dashboard "{}" for {}'.format(self.title, self.tenant.name)


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
