from django.db.models import QuerySet, Count


class TagQuerySet(QuerySet):
    def all_of_type(self, type):
        return self.filter(type=type)

    def get_or_create_all(self, type, tag_names):
        result = list()
        if tag_names:
            if not isinstance(tag_names, (list, tuple, set)):
                tag_names = (tag_names,)

            for tag_name in tag_names:
                tag, created = self.get_or_create(type=type, name=tag_name)
                result.append(tag)

        return result

    def get_solution_tags_info(self, project_id):
        tags_for_project = self.solution_tags_for_project(project_id)
        return list(tags_for_project.annotate(count_cases=Count('solution_respondent_cases'))
                    .values('name', 'count_cases'))

    def get_issue_tags_info(self, project_id):
        tags_for_project = self.issue_tags_for_project(project_id)
        return list(tags_for_project.annotate(count_cases=Count('issue_respondent_cases'))
                    .values('name', 'count_cases'))

    def solution_tags_for_project(self, project_id):
        return self.filter(solution_respondent_cases__respondent__evaluation__project_id=project_id)

    def issue_tags_for_project(self, project_id):
        return self.filter(issue_respondent_cases__respondent__evaluation__project_id=project_id)
