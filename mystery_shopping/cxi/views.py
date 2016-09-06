from rest_framework import status
from rest_framework import views
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_condition import Or

from .algorithms import collect_data_for_overview_dashboard
from .algorithms import get_project_indicator_questions_list
from .algorithms import get_company_indicator_questions_list
from .models import CodedCauseLabel
from .models import CodedCause
from .models import ProjectComment
from .serializers import QuestionWithWhyCausesSerializer
from .algorithms import CollectDataForIndicatorDashboard
from .models import WhyCause
from .serializers import WhyCauseSerializer
from .serializers import CodedCauseLabelSerializer
from .serializers import CodedCauseSerializer
from .serializers import ProjectCommentSerializer

from mystery_shopping.questionnaires.models import QuestionnaireQuestion

from mystery_shopping.projects.models import Project
from mystery_shopping.companies.models import Company

from mystery_shopping.users.permissions import IsCompanyProjectManager, IsCompanyManager
from mystery_shopping.users.permissions import IsTenantProductManager
from mystery_shopping.users.permissions import IsTenantProjectManager


class CodedCauseLabelViewSet(viewsets.ModelViewSet):
    queryset = CodedCauseLabel.objects.all()
    serializer_class = CodedCauseLabelSerializer


class CodedCauseViewSet(viewsets.ModelViewSet):
    queryset = CodedCause.objects.all()
    serializer_class = CodedCauseSerializer

    def create(self, request, *args, **kwargs):
        # add tenant from the request.user to the request.data that is sent to the Coded CauseSerializer
        request.data['tenant'] = request.user.tenant.id
        request.data['coded_label']['tenant'] = request.user.tenant.id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ProjectCommentViewSet(viewsets.ModelViewSet):
    queryset = ProjectComment.objects.all()
    serializer_class = ProjectCommentSerializer


class OverviewDashboard(views.APIView):
    """

    """
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsCompanyProjectManager, IsCompanyManager),)

    def get(self, request, *args, **kwargs):
        project_id = request.query_params.get('project', None)
        entity_id = request.query_params.get('entity', None)
        # section_id = request.query_params.get('section', None)

        if project_id:
            if entity_id is not None and not entity_id.isdigit():

                return Response({
                    'detail': 'Entity param is invalid'
                }, status.HTTP_400_BAD_REQUEST)
            try:
                project = Project.objects.get(pk=project_id)
                if request.user.tenant != project.tenant:
                    return Response({'detail': 'You do not have permission to access to this project.'},
                                    status.HTTP_403_FORBIDDEN)

                response = collect_data_for_overview_dashboard(project, entity_id)

                return Response(response, status.HTTP_200_OK)

            except (Project.DoesNotExist, ValueError):
                return Response({'detail': 'No Project with this id exists or invalid project parameter'},
                                status.HTTP_404_NOT_FOUND)
        return Response({
            'detail': 'Project param is invalid or was not provided'
        }, status.HTTP_400_BAD_REQUEST)


class IndicatorDashboard(views.APIView):
    """
    View that returns indicator data for indicator type

    It computes data like general scores and detailed scores (per answer choice)

    :param project: will filter all questionnaires that are from this project
    :param indicator: can be anything
    """

    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsCompanyProjectManager, IsCompanyManager),)

    def get(self, request, *args, **kwargs):
        project_id = request.query_params.get('project', None)
        entity_id = request.query_params.get('entity', None)
        company_id = request.query_params.get('company', None)
        # section_id = request.query_params.get('section', None)
        indicator_type = request.query_params.get('indicator', None)
        project = None

        if project_id is None:
            if request.user.is_client_user():
                company = request.user.user_company()
                project = Project.objects.get_latest_project_for_client_user(tenant=request.user.tenant, company=company)
            elif request.user.is_tenant_user() and company_id is not None:
                project = Project.objects.get_latest_project_for_client_user(tenant=request.user.tenant, company=company_id)
        elif project_id:
            if entity_id is not None and not entity_id.isdigit():
                return Response({
                    'detail': 'Entity param is invalid'
                }, status.HTTP_400_BAD_REQUEST)
            try:
                project = Project.objects.get(pk=project_id)
            except (Project.DoesNotExist, ValueError):
                return Response({'detail': 'No Project with this id exists or invalid project parameter'},
                                status.HTTP_404_NOT_FOUND)

            if request.user.tenant != project.tenant:
                return Response({'detail': 'You do not have permission to access to this project.'},
                                status.HTTP_403_FORBIDDEN)
        else:
            return Response({
                'detail': 'Unknown (project) error'
            }, status.HTTP_400_BAD_REQUEST)

        if project is not None:
            response = CollectDataForIndicatorDashboard(project, entity_id, indicator_type).build_response()

            return Response(response, status.HTTP_200_OK)

        return Response({
            'detail': 'Project was not provided'
        }, status.HTTP_400_BAD_REQUEST)


class IndicatorDashboardList(views.APIView):
    """

    """
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsCompanyProjectManager, IsCompanyManager),)

    def get(self, request, *args, **kwargs):
        project_id = request.query_params.get('project', None)
        company_id = request.query_params.get('company', None)

        # Since the company parameter "incapsulates" the project one
        # it would be better to check for it first
        if company_id:
            try:
                company = Company.objects.get(pk=company_id)
            except (Company.DoesNotExist , ValueError):
                return Response({'detail': 'No Company with this id exists or invalid company parameter'},
                                status.HTTP_404_NOT_FOUND)
            response = get_company_indicator_questions_list(company)
            return Response(response, status.HTTP_200_OK)

        elif project_id:
            try:
                project = Project.objects.get(pk=project_id)
            except (Project.DoesNotExist, ValueError):
                return Response({'detail': 'No Project with this id exists or invalid project parameter'},
                                status.HTTP_404_NOT_FOUND)

            response = get_project_indicator_questions_list(project)
            return Response(response, status.HTTP_200_OK)

        else:
            return Response({'detail': 'No query parameters were provided'}, status.HTTP_400_BAD_REQUEST)

class WhyCauseViewSet(viewsets.ModelViewSet):
    """

    """
    queryset = WhyCause.objects.all()
    serializer_class = WhyCauseSerializer
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsCompanyProjectManager, IsCompanyManager),)
    encode_serializer_class = QuestionWithWhyCausesSerializer

    @list_route(['get', 'put'])
    def encode(self, request):
        project_id = request.query_params.get('project', None)
        pre_response = self._pre_process_request(project_id, request.user)
        if pre_response:
            return Response(**pre_response)

        response = dict()
        if request.method == 'GET':
            response = self._encode_get(project_id)

        elif request.method == 'PUT':
            response = self._encode_put(project_id, request.data)

        return Response(**response)

    def _pre_process_request(self, project_id, user):
        if project_id is None:
            return dict(status=status.HTTP_400_BAD_REQUEST)
        try:
            project = Project.objects.get(pk=project_id)
        except Project.DoesNotExist:
            return dict(data='Project does not exist',
                        status=status.HTTP_400_BAD_REQUEST)

        if user.tenant != project.tenant:
            return dict(data='You do not have access to this project',
                        status=status.HTTP_400_BAD_REQUEST)

        return False

    def _encode_get(self, project_id):
        questions = QuestionnaireQuestion.objects.get_project_questions(project_id)
        serializer = self.encode_serializer_class(questions, many=True)
        return dict(data=serializer.data, status=status.HTTP_200_OK)

    def _encode_put(self, project_id, data):
        # import ipdb; ipdb.set_trace()
        why_causes_changes = {x['id']: x.get('coded_causes', []) for x in data}
        why_causes = WhyCause.objects.filter(pk__in=why_causes_changes.keys(),
                                             question__questionnaire__evaluation__project=project_id)
        for why_cause in why_causes:
            why_cause.coded_causes.clear()
            coded_cause_ids = why_causes_changes[why_cause.id]

            validated_coded_causes_list = list()
            for id in coded_cause_ids:
                if CodedCause.objects.filter(pk=id).exists():
                    validated_coded_causes_list.append(id)
            why_cause.coded_causes.set(validated_coded_causes_list)

        return dict(status=status.HTTP_200_OK)
