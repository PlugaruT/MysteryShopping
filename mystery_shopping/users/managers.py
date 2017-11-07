from django.contrib.auth.models import UserManager
from django.db.models import QuerySet
from django.db.models.aggregates import Count


class UserQuerySet(QuerySet, UserManager):
    def get_cases_info(self, project_id):
        return list(self.filter(respondent_cases_responsible_for__respondent__evaluation__project_id=project_id)
                    .annotate(count_cases=Count('respondent_cases_responsible_for'))
                    .filter(count_cases__gt=0).values('first_name', 'last_name', 'count_cases'))
