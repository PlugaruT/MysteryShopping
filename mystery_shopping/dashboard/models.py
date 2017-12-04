from django.utils import timezone
from django.db import models

from mystery_shopping.companies.models import CompanyElement
from mystery_shopping.mystery_shopping_utils.models import TenantModel
from mystery_shopping.users.models import User


class DashboardTemplate(TenantModel):
    """
    Model for storing the user defined dashboard structure
    """
    # Relations
    company_element = models.ForeignKey(CompanyElement)
    modified_by = models.ForeignKey(User)
    users = models.ManyToManyField(User, related_name='have_access')

    # Attributes
    is_published = models.BooleanField(default=False)
    modified_date = models.DateTimeField(default=timezone.now)
    title = models.CharField(max_length=120)
    widgets = models.TextField()

    def __str__(self):
        return 'Dashboard "{}" for {}'.format(self.title, self.tenant.name)


class DashboardComment(models.Model):
    """
    Model that will be displayed in a dashboard card
    """
    # Relations
    dashboard = models.ForeignKey(DashboardTemplate, related_name='dashboard_comments')

    # Attributes
    comment = models.TextField()
    title = models.CharField(max_length=30, null=True, blank=True)

    def __str__(self):
        return 'Dashboard Comment: {}'.format(self.title)
