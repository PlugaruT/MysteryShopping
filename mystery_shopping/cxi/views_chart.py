from django.shortcuts import get_object_or_404
from rest_condition import Or
from rest_framework import status
from rest_framework import views
from rest_framework.response import Response

from mystery_shopping.cxi.algorithms import compute_cxi_score_per_company_element
from mystery_shopping.projects.models import Project
from mystery_shopping.users.permissions import IsTenantProductManager, IsTenantProjectManager, \
    IsCompanyProjectManager, IsCompanyManager, IsCompanyEmployee


class CXIPerCompanyElement(views.APIView):
    """
    View that returns computed cxi score per company element
    from a project

    Query params:

     * `project`: **required**, project id for filtering evaluations
    """

    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsCompanyProjectManager,
                             IsCompanyManager, IsCompanyEmployee),)

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
