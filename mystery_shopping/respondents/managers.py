from django.db.models import QuerySet

from mystery_shopping.common.models import Tag


class RespondentCaseQuerySet(QuerySet):
    issue_tag_type = 'RESPONDENT_CASE_ISSUE'
    solution_tag_type = 'RESPONDENT_CASE_SOLUTION'
    follow_up_tag_type = 'RESPONDENT_CASE_FOLLOW_UP'

    def all_issue_tag_options(self):
        return Tag.objects.filter(type=self.issue_tag_type)

    def all_solution_tag_options(self):
        return Tag.objects.filter(type=self.issue_tag_type)

    def all_follow_up_tag_options(self):
        return Tag.objects.filter(type=self.follow_up_tag_type)

    def get_or_create_issue_tag(self, tag_name):
        return Tag.objects.get_or_create(type=self.issue_tag_type, name=tag_name)

    def get_or_create_solution_tag(self, tag_name):
        return Tag.objects.get_or_create(type=self.solution_tag_type, name=tag_name)

    def get_or_create_follow_up_tag(self, tag_name):
        return Tag.objects.get_or_create(type=self.follow_up_tag_type, name=tag_name)
