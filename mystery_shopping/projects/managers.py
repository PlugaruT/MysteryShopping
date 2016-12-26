# -*- coding: utf-8 -*-

from django.db.models.query import QuerySet

from mystery_shopping.projects.constants import EvaluationStatus


class ProjectQuerySet(QuerySet):
    def current_projects_for_a_shopper(self, shopper):
        """Return projects assigned to a specific Shopper that are active now.
        """
        return self.filter(shoppers=shopper)

    def get_projects_for_a_collector(self, shopper):
        """Return projects assigned to a specific Collector that are active now.
        """
        return self.filter(shoppers=shopper) if shopper.is_collector else []

    def get_project_type(self, project_id):
        """Return the type of the provided project.
        """
        return self.get(pk=project_id).type

    def get_latest_project_for_client_user(self, tenant, company):
        """Return the latest project for which to extract and show data on dashboard.
        """
        return self.filter(tenant=tenant, company=company).latest('period_start')

class EvaluationQuerySet(QuerySet):
    def get_project_evaluations(self, project, company):
        """Return list of evaluations that belong to a project
        """
        return self.filter(project=project, project__company=company)

    def get_completed_project_evaluations(self, project, company):
        """Return list of evaluations that belong to a project
        """
        return self.get_project_evaluations(project=project, company=company).filter(status=EvaluationStatus.APPROVED)
