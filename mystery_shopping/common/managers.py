from django.db.models import QuerySet
from django.db.models.aggregates import Count


class TagQuerySet(QuerySet):
    def get_solution_tags_info(self):
        return list(self._count_related_name('solution_respondent_cases').values('name', 'count_cases'))

    def get_issue_tags_info(self):
        return list(self._count_related_name('issue_respondent_cases').values('name', 'count_cases'))

    def _count_related_name(self, related_name):
        """
        Find a better name :D :D
        waiting for code review for better suggestions
        """
        return self.annotate(count_cases=Count(related_name))
