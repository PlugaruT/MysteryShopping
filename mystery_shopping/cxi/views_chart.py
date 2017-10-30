from collections import defaultdict
from django.shortcuts import get_object_or_404
from rest_condition import Or
from rest_framework import status, views
from rest_framework.response import Response

from mystery_shopping.companies.models import CompanyElement
from mystery_shopping.cxi.algorithms import calculate_indicator_score, compute_cxi_score_per_company_element
from mystery_shopping.projects.models import Project
from mystery_shopping.questionnaires.models import QuestionnaireQuestion
from mystery_shopping.users.permissions import IsCompanyEmployee, IsCompanyManager, IsCompanyProjectManager, \
    IsTenantConsultant, IsTenantProductManager, IsTenantProjectManager


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
        response = list()

        if company_id is None:
            return Response({'detail': 'Company param is invalid or was not provided'}, status.HTTP_400_BAD_REQUEST)

        company = get_object_or_404(CompanyElement, pk=company_id, parent=None)

        if request.user.tenant != company.tenant:
            return Response({'detail': 'You do not have permission to access to this resource.'},
                            status.HTTP_403_FORBIDDEN)

        project_list = company.list_of_projects()
        projects_details = defaultdict(list)
        for project in project_list:
            project_places = CompanyElement.objects.filter(id__in=project.get_company_elements_with_evaluations())
            for place in project_places:
                projects_details[project.name].append(
                    self.get_indicator_scores_for_place(project, indicator_name, place))

        for project, project_data in projects_details.items():
            indicator_for_project = defaultdict(list)
            indicator_for_project['key'] = project
            for place in project_data:
                indicator_score = calculate_indicator_score(place['scores'])['indicator']
                indicator_for_project['values'].append(self.build_point(place['place_name'], indicator_score))
            response.append(indicator_for_project)

        return Response(response, status.HTTP_200_OK)

    def get_indicator_scores_for_place(self, project, indicator_name, place):
        return {
            'place_name': place.element_name,
            'scores': list(self.get_questions_scores_for_place(project, indicator_name, place))
        }

    @staticmethod
    def get_questions_scores_for_place(project, indicator_name, place):
        return QuestionnaireQuestion.objects.indicator_questions_for_company_element(project, indicator_name, place) \
            .values_list('score', flat=True)

    @staticmethod
    def build_point(label, value):
        return {
            'label': label,
            'value': value
        }
