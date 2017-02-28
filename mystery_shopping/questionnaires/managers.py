from django.db.models.query import QuerySet

from mystery_shopping.projects.constants import EvaluationStatus, ProjectType
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

    def get_project_questionnaires_for_subdivision(self, project, company_element=None):
        questionnaires = self.get_project_submitted_or_approved_questionnaires(project)
        if company_element is not None:
            questionnaires = questionnaires.filter(evaluation__company_element=company_element)
        return questionnaires

    def get_questionnaires_for_company(self, company):
        return self.filter(evaluation__project__company=company)


class QuestionnaireQuestionQuerySet(QuerySet):
    def get_project_indicator_questions(self, project):
        return self.select_related('questionnaire', 'questionnaire__evaluation__project__company',
                                   'questionnaire__evaluation__company_element').prefetch_related(
            'why_causes', 'why_causes__coded_causes',
            'why_causes__coded_causes__coded_label').filter(questionnaire__evaluation__project=project,
                                                            type=QuestionType.INDICATOR_QUESTION)

    def get_project_specific_indicator_questions(self, project, indicator):
        return self.get_project_indicator_questions(project).filter(additional_info=indicator)

    def get_indicator_questions_for_company_elements(self, project, indicator, company_elements=None):
        if company_elements:
            return self.get_project_specific_indicator_questions(project, indicator).filter(
                questionnaire__evaluation__company_element__in=company_elements)
        else:
            return self.get_project_specific_indicator_questions(project, indicator)


class QuestionnaireTemplateQuestionQuerySet(QuerySet):
    def is_question_editable(self, pk):
        try:
            return self.get(questionnaire_template__type=ProjectType.CUSTOMER_EXPERIENCE_INDEX, pk=pk)
        except:
            return None


class CustomWeightQuerySet(QuerySet):
    def get_custom_weights_for_questionnaire(self, questionnaire_pk, name):
        return self.filter(question__questionnaire_template=questionnaire_pk, name=name)
