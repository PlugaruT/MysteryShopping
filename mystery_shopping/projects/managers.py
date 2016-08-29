# -*- coding: utf-8 -*-
import datetime

from django.db.models.query import QuerySet


class ProjectQuerySet(QuerySet):
    def current_projects_for_a_shopper(self, shopper):
        """Return projects assigned to a specific Shopper that are active now.
        """
        return self.filter(shoppers=shopper)

    def current_projects_for_a_collector(self, collector):
        """Return projects assigned to a specific Collector that are active now.
        """
        if collector.is_collector:
            return self.current_projects_for_a_shopper(collector)
        else:
            return []

    def get_project_type(self, project_id):
        """Return the type of the provided project.
        """
        return self.get(pk=project_id).type

    def get_latest_project_for_client_user(self, tenant, company):
        """Return the latest project for which to extract and show data on dashboard.
        """
        return self.filter(tenant=tenant, company=company).latest('period_start')
