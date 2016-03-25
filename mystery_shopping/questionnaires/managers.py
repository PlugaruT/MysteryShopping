from django.db.models.query import QuerySet


class QuestionnaireQuerySet(QuerySet):
    def get_project_questionnaires(self, template_questionnaire, project):
        return self.filter(template=template_questionnaire,
                           evaluation__project=project)