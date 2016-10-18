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

    def get_project_questionnaires_for_subdivision(self, project, department, entity):
        questionnaires = self.get_project_questionnaires(project)
        if entity is not None:
            questionnaires = questionnaires.filter(evaluation__entity=entity)
        elif department is not None:
            questionnaires = questionnaires.filter(evaluation__entity__department=department)
        return questionnaires


class QuestionnaireQuestionQuerySet(QuerySet):
    def get_project_indicator_questions(self, project):
        return self.filter(questionnaire__evaluation__project=project,
                           type=QuestionType.INDICATOR_QUESTION)

    def get_project_specific_indicator_questions(self, project, indicator):
        return self.get_project_indicator_questions(project).filter(additional_info=indicator)
