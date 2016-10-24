from django.test.testcases import TestCase

from mystery_shopping.factories.companies import EntityFactory
from mystery_shopping.factories.projects import ProjectFactory, ResearchMethodologyFactory, EvaluationFactory
from mystery_shopping.factories.questionnaires import QuestionnaireTemplateFactory, QuestionnaireFactory
from mystery_shopping.questionnaires.models import Questionnaire


class GetProjectQuestionnaires(TestCase):
    def setUp(self):
        self.project = ProjectFactory.create()
        self.questionnaire = QuestionnaireFactory.create()
        EvaluationFactory.create(project=self.project, questionnaire=self.questionnaire)

    def test_with_project_and_without_questionnaire_template(self):
        self.assertEquals(self._result(), [])

    def test_with_project_and_with_questionnaire_template(self):
        # Dependency between QuestionnaireTemplate and ResearchMethodology
        research_methodology = ResearchMethodologyFactory.create()
        questionnaire_template = QuestionnaireTemplateFactory.create()
        research_methodology.questionnaires.add(questionnaire_template)

        # Dependency between Project and ResearchMethodology
        self.project.research_methodology = research_methodology
        self.project.save()

        # Dependency between Questionnaire and QuestionnaireTemplate
        self.questionnaire.template = questionnaire_template
        self.questionnaire.save()

        self.assertEquals(self._result(), [self.questionnaire])

    def _result(self):
        return list(Questionnaire.objects.get_project_questionnaires(project=self.project))


class GetProjectQuestionnairesForEntity(TestCase):
    def setUp(self):
        # Dependency between QuestionnaireTemplate and ResearchMethodology
        questionnaire_template = QuestionnaireTemplateFactory.create()
        research_methodology = ResearchMethodologyFactory.create()
        research_methodology.questionnaires.add(questionnaire_template)

        # Dependency between Project and ResearchMethodology
        self.project = ProjectFactory.create(research_methodology=research_methodology)

        # Dependency between Project Evaluation and Questionnaire
        self.questionnaire1 = QuestionnaireFactory.create(template=questionnaire_template, title='first')
        self.evaluation1 = EvaluationFactory.create(project=self.project, questionnaire=self.questionnaire1)
        self.questionnaire2 = QuestionnaireFactory.create(template=questionnaire_template, title='second')
        self.evaluation2 = EvaluationFactory.create(project=self.project, questionnaire=self.questionnaire2)

    def test_2_questionnaires_and_entity_is_linked_to_first_questionnaire(self):
        entity = EntityFactory.create()

        # Link to the first questionnaire
        self.evaluation1.entity = entity
        self.evaluation1.save()

        self.assertEquals(self._result(entity), [self.questionnaire1])

    def test_2_questionnaires_when_both_are_linked_to_entities(self):
        entity = EntityFactory.create()

        # Link to the first questionnaire
        self.evaluation1.entity = entity
        self.evaluation1.save()

        # Link to the second questionnaire
        self.evaluation2.entity = entity
        self.evaluation2.save()

        self.assertCountEqual(self._result(entity), [self.questionnaire1, self.questionnaire2])

    def test_2_questionnaires_when_none_are_linked_to_entity(self):
        entity = EntityFactory.create()
        self.assertEquals(self._result(entity), [])

    def test_2_questionnaires_when_entity_is_none(self):
        self.assertCountEqual(self._result(None), [self.questionnaire1, self.questionnaire2])

    def _result(self, entity):
        return list(Questionnaire.objects.get_project_questionnaires_for_subdivision(project=self.project, entity=entity))
