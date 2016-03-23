# -*- coding: utf-8 -*-
import datetime

from django.db.models.query import QuerySet


class ProjectQuerySet(QuerySet):
    def current_projects_for_a_shopper(self, shopper):
        """Return projects assigned to a specific Shopper that are active now.
        """
        today = datetime.date.today()
        return self.filter(shoppers=shopper,
                           period_start__gte=today,
                           period_end__lte=today)

    def current_projects_for_a_collector(self, collector):
        """Return projects assigned to a specific Collector that are active now.
        """
        return self.current_projects_for_a_shopper(collector).filter(shoppers__is_collector=True)