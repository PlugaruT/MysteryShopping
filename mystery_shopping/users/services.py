from mystery_shopping.companies.serializers import EntitySerializer, SectionSerializer, DepartmentSerializer
from mystery_shopping.projects.models import Project
from mystery_shopping.questionnaires.serializers import QuestionnaireTemplateSerializer


class ShopperService:

    def __init__(self, shopper):
        self.shopper = shopper

    def get_available_list_of_places_with_questionnaires(self):
        '''Return the list of places available for a Collector to evaluate.
        '''
        projects = Project.objects.get_projects_for_a_collector(self.shopper)

        return list(map(get_projects_with_evaluations, projects))


def get_projects_with_evaluations(project):
    return {
        'project': project.pk,
        'project_start_date': project.period_start,
        'project_end_date': project.period_end,
        'places_with_questionnaires': get_list_of_places_with_questionnaires_for_a_project(project)
    }


def get_list_of_places_with_questionnaires_for_a_project(project):
    '''Return the list of Entities for a specific project with corresponding questionnaires.
    '''
    result = list()
    questionnaire = project.research_methodology.questionnaires.first()
    places_to_assess = project.research_methodology.places_to_assess.all()

    place_serializer_dispatcher = {
        'entity': EntitySerializer,
        'section': SectionSerializer,
        'department': DepartmentSerializer
    }

    for place_to_assess in places_to_assess:
        result.append({
            'project': project.pk,
            'entity_repr': place_serializer_dispatcher[place_to_assess.place_type.name](place_to_assess.place).data,
            'questionnaire': QuestionnaireTemplateSerializer(questionnaire).data,
            'questionnaire_template': questionnaire.id
        })

    return result
