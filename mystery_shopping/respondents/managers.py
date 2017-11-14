from django.db.models import QuerySet
from django.db.models.aggregates import Count


class RespondentCaseQuerySet(QuerySet):
    pass


class RespondentQuerySet(QuerySet):
    def without_cases(self):
        return self.annotate(cases_count=Count('respondent_cases')).filter(cases_count=0)

    def with_cases(self):
        return self.annotate(cases_count=Count('respondent_cases')).filter(cases_count__gt=0)
