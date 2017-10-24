from django.db.models import QuerySet
from django.db.models.aggregates import Count

from mystery_shopping.common.models import Tag


class RespondentCaseQuerySet(QuerySet):
    ISSUE_TAG_TYPE = 'RESPONDENT_CASE_ISSUE'
    SOLUTION_TAG_TYPE = 'RESPONDENT_CASE_SOLUTION'
    FOLLOW_UP_TAG_TYPE = 'RESPONDENT_CASE_FOLLOW_UP'

    def all_issue_tag_options(self):
        return Tag.objects.filter(type=self.ISSUE_TAG_TYPE)

    def all_solution_tag_options(self):
        return Tag.objects.filter(type=self.ISSUE_TAG_TYPE)

    def all_follow_up_tag_options(self):
        return Tag.objects.filter(type=self.FOLLOW_UP_TAG_TYPE)

    def get_or_create_issue_tag(self, tag_name):
        return Tag.objects.get_or_create(type=self.ISSUE_TAG_TYPE, name=tag_name)

    def get_or_create_solution_tag(self, tag_name):
        return Tag.objects.get_or_create(type=self.SOLUTION_TAG_TYPE, name=tag_name)

    def get_or_create_follow_up_tag(self, tag_name):
        return Tag.objects.get_or_create(type=self.FOLLOW_UP_TAG_TYPE, name=tag_name)

    def get_cases_per_state(self):
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
        result = list(self.values('state').annotate(count=Count('id')))
        result.extend(list(filter(lambda d: d['state'] not in [d['state'] for d in result], default_response)))
        return result
