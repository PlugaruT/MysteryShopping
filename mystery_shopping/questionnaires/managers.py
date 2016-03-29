from django.db.models.query import QuerySet


class QuestionnaireQuerySet(QuerySet):
    def get_project_questionnaires(self, project):
        template_questionnaire = project.research_methodology.questionnaires.first()
        return self.filter(template=template_questionnaire,
                           evaluation__project=project)#.select_related('')