from collections import defaultdict

from rest_framework import status
from rest_framework import views
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_condition import Or

from .algorithms import group_questions_by_answer
from .algorithms import get_indicator_scores
from .algorithms import calculate_indicator_score
from .algorithms import calculate_overview_score
from .algorithms import get_indicator_details
from .algorithms import collect_data_for_indicator_dashboard
from .algorithms import collect_data_for_overview_dashboard
from .models import CodedCauseLabel
from .models import CodedCause
from .models import ProjectComment
from mystery_shopping.nps.serializers import QuestionnaireQuestionToEncodeSerializer
from mystery_shopping.questionnaires.models import QuestionnaireQuestion
from .serializers import CodedCauseLabelSerializer
from .serializers import CodedCauseSerializer
from .serializers import ProjectCommentSerializer

# from mystery_shopping.questionnaires.models import QuestionnaireTemplate
from mystery_shopping.projects.models import Project
# from mystery_shopping.questionnaires.models import Questionnaire
from mystery_shopping.questionnaires.constants import IndicatorQuestionType

from mystery_shopping.users.permissions import IsCompanyProjectManager, IsCompanyManager
from mystery_shopping.users.permissions import IsTenantProductManager
from mystery_shopping.users.permissions import IsTenantProjectManager


class CodedCauseLabelViewSet(viewsets.ModelViewSet):
    queryset = CodedCauseLabel.objects.all()
    serializer_class = CodedCauseLabelSerializer


class CodedCauseViewSet(viewsets.ModelViewSet):
    queryset = CodedCause.objects.all()
    serializer_class = CodedCauseSerializer
    question_serializer_class = QuestionnaireQuestionToEncodeSerializer

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
            try:
                project = Project.objects.get(pk=project_id)
                if request.user.tenant != project.tenant:
                    return Response({'detail': 'You do not have permission to access to this project.'},
                                    status.HTTP_403_FORBIDDEN)

                response = collect_data_for_overview_dashboard(project, entity_id)

                return Response(response, status.HTTP_200_OK)

            except Project.DoesNotExist:
                return Response({'detail': 'No Project with this id exists'},
                                status.HTTP_404_NOT_FOUND)
        return Response({
            'detail': 'Project was not provided'
        }, status.HTTP_400_BAD_REQUEST)


class IndicatorDashboard(views.APIView):
    """
    View that returns indicator data for indicator type

    It computes data like general scores and detailed scores (per answer choice)

    :param project: will filter all questionnaires that are from this project
    :param indicator: can be 'n', 'j', 'e' or 'u'
    """

    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsCompanyProjectManager, IsCompanyManager),)

    def get(self, request, *args, **kwargs):
        project_id = request.query_params.get('project', None)
        entity_id = request.query_params.get('entity', None)
        company_id = request.query_params.get('company', None)
        # section_id = request.query_params.get('section', None)
        indicator_type = request.query_params.get('indicator', None)
        project = None

        # As this requires no database hit, check if indicator sent is a valid one
        if indicator_type not in IndicatorQuestionType.INDICATORS_LIST:
            return Response({'detail': 'Indicator type sent is not a valid option'})

        if project_id is None:
            if request.user.is_client_user():
                company = request.user.user_company()
                project = Project.objects.get_latest_project_for_client_user(tenant=request.user.tenant, company=company)
            elif request.user.is_tenant_user() and company_id is not None:
                project = Project.objects.get_latest_project_for_client_user(tenant=request.user.tenant, company=company_id)
        else:
            try:
                project = Project.objects.get(pk=project_id)
            except Project.DoesNotExist:
                return Response({'detail': 'No Project with this id exists'},
                                status.HTTP_404_NOT_FOUND)

            if request.user.tenant != project.tenant:
                return Response({'detail': 'You do not have permission to access to this project.'},
                                status.HTTP_403_FORBIDDEN)

        if project is not None:
            response = collect_data_for_indicator_dashboard(project, entity_id, indicator_type)

            return Response(response, status.HTTP_200_OK)

        return Response({
            'detail': 'Project was not provided'
        }, status.HTTP_400_BAD_REQUEST)