from django.shortcuts import get_object_or_404
from rest_condition import Or
from rest_framework import status
from rest_framework import views
from rest_framework.response import Response

from mystery_shopping.companies.models import CompanyElement
from mystery_shopping.cxi.algorithms import compute_cxi_score_per_company_element, calculate_indicator_score
from mystery_shopping.projects.models import Project
from mystery_shopping.questionnaires.constants import QuestionType
from mystery_shopping.questionnaires.models import QuestionnaireQuestion
from mystery_shopping.users.permissions import IsTenantProductManager, IsTenantProjectManager, \
    IsCompanyProjectManager, IsCompanyManager, IsCompanyEmployee, IsTenantConsultant


class CXIPerCompanyElement(views.APIView):
    """
    View that returns computed cxi score per company element
    from a project

    Query params:

     * `project`: **required**, project id for filtering evaluations
    """

    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsCompanyProjectManager,
                             IsTenantConsultant, IsCompanyProjectManager, IsCompanyManager, IsCompanyEmployee),)

    def get(self, request, *args, **kwargs):
        project_id = request.query_params.get('project', None)

        if project_id is None:
            return Response({'detail': 'Project param is invalid or was not provided'}, status.HTTP_400_BAD_REQUEST)

        project = get_object_or_404(Project, pk=project_id)
        if request.user.tenant != project.tenant:
            return Response({'detail': 'You do not have permission to access to this project.'},
                            status.HTTP_403_FORBIDDEN)

        raw_data = compute_cxi_score_per_company_element(project)
        response = self.cxi_data_per_company_element(raw_data)
        return Response(response, status.HTTP_200_OK)

    def cxi_data_per_company_element(self, data_per_company_element):
        result = list()
        template_item = next(iter(data_per_company_element))
        template_values = data_per_company_element[template_item]
        for cxi_name in template_values:
            series = dict()
            series['values'] = list()
            series['key'] = cxi_name
            for company_element, cxi_data in data_per_company_element.items():
                series['values'].append(self.build_data_point(company_element, cxi_data[cxi_name]))
            result.append(series)
        return result

    @staticmethod
    def build_data_point(label, value):
        return {
            "label": label,
            "value": value
        }


class IndicatorPerCompanyElement(views.APIView):
    """

    """
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsCompanyProjectManager,
                             IsTenantConsultant, IsCompanyProjectManager, IsCompanyManager, IsCompanyEmployee),)

    def get(self, request, *args, **kwargs):
        company_id = request.query_params.get('company', None)
        indicator_name = request.query_params.get('indicator', None)
        if company_id is None:
            return Response({'detail': 'Company param is invalid or was not provided'}, status.HTTP_400_BAD_REQUEST)

        company = get_object_or_404(CompanyElement, pk=company_id, parent=None)

        if request.user.tenant != company.tenant:
            return Response({'detail': 'You do not have permission to access to this project.'},
                            status.HTTP_403_FORBIDDEN)

        project_list = company.projects.all()
        data = dict()
        for project in project_list:
            data[project.name] = list()
            project_places = CompanyElement.objects.filter(id__in=project.get_company_elements_with_evaluations())
            for place in project_places:
                place_scores = QuestionnaireQuestion.objects.indicator_questions_for_company_element(project,
                                                                                                     indicator_name,
                                                                                                     place) \
                    .values_list('score', flat=True)
                data[project.name].append({
                    'place_name': place.element_name,
                    'scores': list(place_scores)
                })
        response = list()
        for project, project_data in data.items():
            temp_dict = dict()
            temp_dict['key'] = project
            temp_dict['values'] = list()
            for place in project_data:
                temp_dict['values'].append({
                    'label': place['place_name'],
                    'value': calculate_indicator_score(place['scores'])['indicator']
                })
            response.append(temp_dict)

        print(response)

        return Response(response, status.HTTP_200_OK)
