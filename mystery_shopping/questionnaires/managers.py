from django.db.models.query import QuerySet


class QuestionnaireQuerySet(QuerySet):
    def get_project_questionnaires(self, project, entity):
        template_questionnaire = project.research_methodology.questionnaires.first()
        if entity:
            return self.filter(template=template_questionnaire,
                               evaluation__project=project,
                               evaluation__entity=entity)

        return self.filter(template=template_questionnaire,
                           evaluation__project=project)#.select_related('')