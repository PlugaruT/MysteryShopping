from django.db.models.query import QuerySet

from mystery_shopping.projects.constants import EvaluationStatus
from mystery_shopping.questionnaires.constants import QuestionType


class QuestionnaireQuerySet(QuerySet):
    def get_project_questionnaires(self, project):
        try:
            template_questionnaire = project.research_methodology.questionnaires.first()
        except AttributeError:
            template_questionnaire = None

        return self.filter(template=template_questionnaire,
                           evaluation__project=project)

    def get_project_submitted_or_approved_questionnaires(self, project):
        try:
            template_questionnaire = project.research_methodology.questionnaires.first()
        except AttributeError:
            template_questionnaire = None

        return self.filter(template=template_questionnaire,
                           evaluation__project=project,
                           evaluation__status__in=[EvaluationStatus.SUBMITTED, EvaluationStatus.APPROVED])

    def get_project_questionnaires_for_subdivision(self, project, department=None, entity=None, section=None):
        questionnaires = self.get_project_submitted_or_approved_questionnaires(project)
        if section is not None:
            questionnaires = questionnaires.filter(evaluation__section=section)
        elif entity is not None:
            questionnaires = questionnaires.filter(evaluation__entity=entity)
        elif department is not None:
            questionnaires = questionnaires.filter(evaluation__entity__department=department)
        return questionnaires

    def get_questionnaires_for_company(self, company):
        return self.filter(evaluation__project__company=company)


class QuestionnaireQuestionQuerySet(QuerySet):
    def get_project_indicator_questions(self, project):
        return self.filter(questionnaire__evaluation__project=project,
                           type=QuestionType.INDICATOR_QUESTION)

    def get_project_specific_indicator_questions(self, project, indicator):
        return self.get_project_indicator_questions(project).filter(additional_info=indicator)
