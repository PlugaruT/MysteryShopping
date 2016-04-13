from mystery_shopping.companies.serializers import EntitySerializer, SectionSerializer
from mystery_shopping.projects.models import Project
from mystery_shopping.questionnaires.serializers import QuestionnaireTemplateSerializer


class ShopperService:

    def __init__(self, shopper):
        self.shopper = shopper

    def get_available_list_of_places_with_questionnaires(self):
        """Return the list of places available for a Collector to evaluate.
        """
        list_of_lists_per_project = list()
        current_projects = Project.objects.current_projects_for_a_collector(self.shopper)

        for project in current_projects:
            list_of_lists_per_project.append(self.get_list_of_places_with_questionnaires_for_a_project(project))

        result = [item for sublist in list_of_lists_per_project for item in sublist]
        return result

    def get_list_of_places_with_questionnaires_for_a_project(self, project):
        """Return the list of Entities for a specific project with corresponding questionnaires.
        """
        result = list()
        questionnaire = project.research_methodology.questionnaires.first()
        places_to_assess = project.research_methodology.places_to_assess.all()

        place_serializer_dispatcher = {
            "entity": EntitySerializer,
            "section": SectionSerializer
        }

        for place_to_assess in places_to_assess:
            result.append({
                "entity_repr": place_serializer_dispatcher[place_to_assess.place_type.name](place_to_assess.place).data,
                "questionnaire": QuestionnaireTemplateSerializer(questionnaire).data,
                "project": project.pk,
                "questionnaire_template": questionnaire.id
            })

        return result
