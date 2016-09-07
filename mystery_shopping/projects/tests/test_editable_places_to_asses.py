from django.contrib.contenttypes.models import ContentType
from django.test.testcases import TestCase

from mystery_shopping.factories.companies import EntityFactory, SectionFactory
from mystery_shopping.factories.projects import EvaluationFactory, ProjectFactory, ResearchMethodologyFactory
from mystery_shopping.factories.questionnaires import QuestionnaireTemplateFactory
from mystery_shopping.projects.models import PlaceToAssess
from mystery_shopping.projects.serializers import ProjectSerializer


class TestProjectEditablePlaces(TestCase):
    def setUp(self):
        self.entity_1 = EntityFactory()
        self.entity_2 = EntityFactory()
        self.section_1 = SectionFactory()
        self.template_questionnaire = QuestionnaireTemplateFactory()
        self.research_methodology = ResearchMethodologyFactory()
        self.research_methodology.questionnaires.add(self.template_questionnaire)
        self.places_to_assess_1 = PlaceToAssess.objects.create(research_methodology=self.research_methodology,
                                                               place_type=ContentType.objects.get_for_model(self.entity_1),
                                                               place_id=self.entity_1.id)
        self.places_to_assess_2 = PlaceToAssess.objects.create(research_methodology=self.research_methodology,
                                                               place_type=ContentType.objects.get_for_model(self.entity_2),
                                                               place_id=self.entity_2.id)
        self.project = ProjectFactory(research_methodology=self.research_methodology)

    def test_create_evaluation_for_one_entity(self):
        evaluation = EvaluationFactory(entity=self.entity_1, project=self.project,
                                       questionnaire_template=self.template_questionnaire)
        serializer = ProjectSerializer(self.project)
        # The list should contain information about self.entity_2
        self.assertEqual(serializer.data.get('editable_places')[0].get('place_id'), self.entity_2.id)

    def test_create_evaluation_for_two_entities(self):
        evaluation_1 = EvaluationFactory(entity=self.entity_1, project=self.project,
                                         questionnaire_template=self.template_questionnaire)
        evaluation_2 = EvaluationFactory(entity=self.entity_2, project=self.project,
                                         questionnaire_template=self.template_questionnaire)
        serializer = ProjectSerializer(self.project)
        # The list should be empty because there are evaluations for each all entities
        self.assertListEqual(serializer.data.get('editable_places'),  [])

    def test_when_there_are_no_evaluations_for_any_entity(self):
        serializer = ProjectSerializer(self.project)
        # Check if the list contains information about 2 entities
        self.assertEquals(len(serializer.data.get('editable_places')), 2)
        # The list should contain information about all entities because there are no evaluation for them
        self.assertEqual(serializer.data.get('editable_places')[0].get('place_id'), self.entity_1.id)
        self.assertEqual(serializer.data.get('editable_places')[1].get('place_id'), self.entity_2.id)

