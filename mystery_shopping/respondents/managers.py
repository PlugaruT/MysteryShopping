from django.db.models import QuerySet
from django.db.models.aggregates import Count


class RespondentCaseQuerySet(QuerySet):
    def get_average_time_per_state(self, project_id):
        return []

    def get_cases_per_state(self, project_id):
        """
        Method returns data about number of cases for each state. If the state doesn't have cases
        It will return that the state has 0
        :return: list of dicts
        """
        default_response = [
            {'state': 'ASSIGNED', 'count': 0},
            {'state': 'ESCALATED', 'count': 0},
            {'state': 'ANAL', 'count': 0},
            {'state': 'IMPLEMENTATION', 'count': 0},
            {'state': 'FOLLOW_UP', 'count': 0},
            {'state': 'SOLVED', 'count': 0},
            {'state': 'CLOSED', 'count': 0},
        ]
        result = list(
            self.filter(respondent__evaluation__project_id=project_id).values('state').annotate(count=Count('id')))
        result.extend(list(filter(lambda d: d['state'] not in [d['state'] for d in result], default_response)))
        return result


class RespondentQuerySet(QuerySet):
    def without_cases(self):
        return self.annotate(cases_count=Count('respondent_cases')).filter(cases_count=0)

    def with_cases(self):
        return self.annotate(cases_count=Count('respondent_cases')).filter(cases_count__gt=0)
