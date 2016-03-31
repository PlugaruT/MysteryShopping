from django.db.models.query import QuerySet

from .constants import IndicatorQuestionType


class QuestionnaireQuerySet(QuerySet):
    def get_project_questionnaires(self, project, entity):
        template_questionnaire = project.research_methodology.questionnaires.first()
        if entity:
            return self.filter(template=template_questionnaire,
                               evaluation__project=project,
                               evaluation__entity=entity)

        return self.filter(template=template_questionnaire,
                           evaluation__project=project)#.select_related('')


class QuestionnaireQuestionQuerySet(QuerySet):
    def get_project_questions(self, project):
        return self.filter(questionnaire__evaluation__project=project,
                           type__in=IndicatorQuestionType.INDICATORS_LIST).prefetch_related('coded_causes')
