from mystery_shopping.companies.serializers import EntitySerializer, SectionSerializer
from mystery_shopping.projects.constants import EvaluationStatus
from mystery_shopping.projects.models import Project
from mystery_shopping.projects.serializers import EvaluationSerializer


class ShopperService:

    def __init__(self, shopper):
        self.shopper = shopper

    def get_available_list_of_places_with_questionnaires(self):
        '''Return the list of places available for a Collector to evaluate.
        '''
        projects = Project.objects.get_projects_for_a_collector(self.shopper)

        return list(map(self.get_projects_with_evaluations, projects))


    def get_projects_with_evaluations(self, project):
        return {
            'project': project.pk,
            'project_start_date': project.period_start,
            'project_end_date': project.period_end,
            'places_with_questionnaires': self.get_list_of_places_with_questionnaires_for_a_project(project)
        }


    def get_list_of_places_with_questionnaires_for_a_project(self, project):
        '''Return the list of Entities for a specific project with corresponding questionnaires.
        '''
        result = list()
        unique_evaluations = project.evaluations\
            .filter(shopper=self.shopper, status=EvaluationStatus.PLANNED)\
            .distinct('entity', 'section').all()

        to_complete_info = list()
        for to_complete in unique_evaluations:
            evaluation_count = dict()
            evaluation_count['evaluation'] = to_complete
            evaluation_count['count'] = project.evaluations\
                .filter(shopper=self.shopper, status=EvaluationStatus.PLANNED,
                        entity=to_complete.entity, section=to_complete.section)\
                .count()
            to_complete_info.append(evaluation_count)

        for to_complete in to_complete_info:
            evaluation = to_complete['evaluation']
            questionnaire = evaluation.questionnaire
            entity_repr = None
            if evaluation.section is not None:
                entity_repr = SectionSerializer(evaluation.section).data
            else:
                entity_repr = EntitySerializer(evaluation.entity).data

            result.append({
                'count': to_complete['count'],
                'entity_repr': entity_repr,
                'evaluation': EvaluationSerializer(evaluation).data
            })

        return result
