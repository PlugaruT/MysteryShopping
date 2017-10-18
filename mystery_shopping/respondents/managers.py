from django.db.models import QuerySet

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
