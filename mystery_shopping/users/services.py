from mystery_shopping.companies.serializers import SimpleCompanyElementSerializer
from mystery_shopping.projects.constants import EvaluationStatus
from mystery_shopping.projects.models import Project
from mystery_shopping.projects.serializers import EvaluationSerializer, EvaluationSerializerGET


class ShopperService:
    def __init__(self, shopper):
        self.shopper = shopper

    def get_available_list_of_places_with_questionnaires(self):
        '''Return the list of places available for a Collector to evaluate.
        '''
        projects = Project.objects.get_planned_projects_for_a_collector(self.shopper)

        return list(map(self.get_projects_with_evaluations, projects))

    def get_projects_with_evaluations(self, project):
        return {
            'project': project.pk,
            'name': project.name,
            'places_with_questionnaires': self.get_list_of_places_with_questionnaires_for_a_project(project)
        }

    def _get_evaluations_and_their_count(self, project, unique_evaluations):
        to_complete_info = list()
        for to_complete in unique_evaluations:
            evaluation_count = dict()
            evaluation_count['evaluation'] = to_complete
            evaluation_count['count'] = project.evaluations.filter(shopper=self.shopper,
                                                                   status=EvaluationStatus.PLANNED,
                                                                   company_element=to_complete.company_element,
                                                                   suggested_start_date=to_complete.suggested_start_date,
                                                                   suggested_end_date=to_complete.suggested_end_date).count()
            to_complete_info.append(evaluation_count)

        return to_complete_info

    def _build_result(self, to_complete_info):
        result = list()
        for to_complete in to_complete_info:
            evaluation = to_complete['evaluation']
            entity = SimpleCompanyElementSerializer(evaluation.company_element).data

            result.append({
                'count': to_complete['count'],
                'entity': entity,
                'evaluation': EvaluationSerializerGET(evaluation).data
            })

        return result

    def get_list_of_places_with_questionnaires_for_a_project(self, project):
        '''Return the list of Entities for a specific project with corresponding questionnaires.
        '''
        unique_evaluations = project.evaluations \
            .filter(shopper=self.shopper, status=EvaluationStatus.PLANNED) \
            .distinct('company_element', 'suggested_start_date', 'suggested_end_date').all()

        to_complete_info = self._get_evaluations_and_their_count(project, unique_evaluations)

        return self._build_result(to_complete_info)
