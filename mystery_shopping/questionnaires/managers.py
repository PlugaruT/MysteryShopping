from django.db.models.query import QuerySet

from mystery_shopping.questionnaires.constants import QuestionType


class QuestionnaireQuerySet(QuerySet):
    def get_project_questionnaires(self, project):
        try:
            template_questionnaire = project.research_methodology.questionnaires.first()
        except AttributeError:
            template_questionnaire = None

        return self.filter(template=template_questionnaire,
                           evaluation__project=project)

    def get_project_questionnaires_for_entity(self, project, entity):
        result = self.get_project_questionnaires(project)
        if entity is not None:
            result = result.filter(evaluation__entity=entity)
        return result


class QuestionnaireQuestionQuerySet(QuerySet):
    def get_project_questions(self, project):
        return self.filter(questionnaire__evaluation__project=project,
                           type=QuestionType.INDICATOR_QUESTION)
