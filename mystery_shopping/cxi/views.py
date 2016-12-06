from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework import views
from rest_framework import viewsets
from rest_framework.decorators import list_route, detail_route
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response
from rest_condition import Or

from mystery_shopping.cxi.algorithms import GetPerDayQuestionnaireData
from mystery_shopping.cxi.serializers import SimpleWhyCauseSerializer
from mystery_shopping.mystery_shopping_utils.paginators import FrustrationWhyCausesPagination, \
    AppreciationWhyCausesPagination
from mystery_shopping.questionnaires.utils import check_interval_date
from .algorithms import CodedCausesPercentageTable
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

from mystery_shopping.users.permissions import IsCompanyProjectManager, IsCompanyManager, IsTenantConsultant
from mystery_shopping.users.permissions import IsTenantProductManager
from mystery_shopping.users.permissions import IsTenantProjectManager


class CodedCauseLabelViewSet(viewsets.ModelViewSet):
    queryset = CodedCauseLabel.objects.all()
    serializer_class = CodedCauseLabelSerializer


class CodedCauseViewSet(viewsets.ModelViewSet):
    queryset = CodedCause.objects.all()
    queryset = CodedCauseSerializer().setup_eager_loading(queryset)
    serializer_class = CodedCauseSerializer

    def get_queryset(self):
        project_id = self.request.query_params.get('project')
        if project_id:
            try:
                project = Project.objects.get(pk=project_id)
                return self.queryset.filter(project=project) if self.request.user.tenant == project.tenant else self.queryset.none()
            except (Project.DoesNotExist, ValueError):
                return self.queryset.none()
        return self.queryset.none()

    def create(self, request, *args, **kwargs):
        # add tenant from the request.user to the request.data that is sent to the Coded CauseSerializer
        request.data['tenant'] = request.user.tenant.id
        request.data['coded_label']['tenant'] = request.user.tenant.id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @list_route(methods=['get'])
    def sorted(self, request):
        serializer = self.get_serializer(self.queryset, many=True)
        response = self.group_by_indicator_and_sentiment(serializer.data)
        return Response(response)

    def group_by_indicator_and_sentiment(self, coded_causes):
        result = dict()
        grouped_by_indicator = self.group_by_indicator(coded_causes)
        for indicator, grouped_coded_causes in grouped_by_indicator.items():
            grouped_by_sentiment = self.group_by_sentiment(grouped_coded_causes)
            result[indicator] = grouped_by_sentiment
        return result

    @staticmethod
    def group_by_indicator(coded_causes):
        result = dict()
        for coded_cause in coded_causes:
            result.setdefault(coded_cause['type'], []).append(coded_cause)
        return result

    @staticmethod
    def group_by_sentiment(coded_causes):
        result = dict()
        for coded_cause in coded_causes:
            result.setdefault(coded_cause['sentiment'], []).append(coded_cause)
        return result


class ProjectCommentViewSet(viewsets.ModelViewSet):
    queryset = ProjectComment.objects.all()
    serializer_class = ProjectCommentSerializer


class CxiIndicatorTimelapse(views.APIView):
    """

    """
    def get(self, request, *args, **kwargs):
        company_id = request.query_params.get('company')
        start, end = check_interval_date(request.query_params)
        response = GetPerDayQuestionnaireData(start, end, company_id).build_response()
        return Response(response, status.HTTP_200_OK)


class OverviewDashboard(views.APIView):
    """

    """
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsCompanyProjectManager, IsCompanyManager),)

    def get(self, request, *args, **kwargs):
        project_id = request.query_params.get('project', None)
        department_id = request.query_params.get('department', None)
        entity_id = request.query_params.get('entity', None)
        section_id = request.query_params.get('section', None)

        parameters_are_valid = self.parameter_is_valid(entity_id) or \
                               self.parameter_is_valid(department_id) or \
                               self.parameter_is_valid(section_id)

        if project_id:
            if parameters_are_valid:

                return Response({
                    'detail': 'Entity param is invalid'
                }, status.HTTP_400_BAD_REQUEST)
            try:
                project = Project.objects.get(pk=project_id)
                if request.user.tenant != project.tenant:
                    return Response({'detail': 'You do not have permission to access to this project.'},
                                    status.HTTP_403_FORBIDDEN)

                response = collect_data_for_overview_dashboard(project, department_id, entity_id, section_id)

                return Response(response, status.HTTP_200_OK)

            except (Project.DoesNotExist, ValueError):
                return Response({'detail': 'No Project with this id exists or invalid project parameter'},
                                status.HTTP_404_NOT_FOUND)
        return Response({
            'detail': 'Project param is invalid or was not provided'
        }, status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def parameter_is_valid(parameter):
        return parameter is not None and not parameter.isdigit()


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
        company_id = request.query_params.get('company', None)
        department_id = request.query_params.get('department', None)
        entity_id = request.query_params.get('entity', None)
        section_id = request.query_params.get('section', None)
        indicator_type = request.query_params.get('indicator', None)
        project = None

        parameters_are_valid = self.parameter_is_valid(entity_id) or \
                               self.parameter_is_valid(department_id) or \
                               self.parameter_is_valid(section_id)

        if project_id is None:
            if request.user.is_client_user():
                company = request.user.user_company()
                project = Project.objects.get_latest_project_for_client_user(tenant=request.user.tenant, company=company)
            elif request.user.is_tenant_user() and company_id is not None:
                project = Project.objects.get_latest_project_for_client_user(tenant=request.user.tenant, company=company_id)
        elif project_id:
            # TODO: handle this in a more elegant way
            if parameters_are_valid:
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
            response = CollectDataForIndicatorDashboard(project, department_id, entity_id, section_id, indicator_type).build_response()

            return Response(response, status.HTTP_200_OK)

        return Response({
            'detail': 'Project was not provided'
        }, status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def parameter_is_valid(parameter):
        return parameter is not None and not parameter.isdigit()


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


class CodedCausePercentage(views.APIView):
    """

    """
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsCompanyProjectManager, IsCompanyManager,
                             IsTenantConsultant),)

    def get(self, request, *args, **kwargs):
        indicator = request.query_params.get('indicator')
        project_id = request.query_params.get('project')
        pre_response = self._pre_process_request(project_id, request.user)
        if pre_response:
            return Response(**pre_response)
        coded_cause_percentage = CodedCausesPercentageTable(indicator, project_id)
        response = coded_cause_percentage.build_response()
        return Response(response, status=status.HTTP_200_OK)

    @staticmethod
    def _pre_process_request(project_id, user):
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


class FrustrationWhyCauseViewSet(ListModelMixin, viewsets.GenericViewSet):
    serializer_class = SimpleWhyCauseSerializer
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsTenantConsultant),)
    pagination_class = FrustrationWhyCausesPagination
    queryset = WhyCause.objects.all()

    def list(self, request, *args, **kwargs):
        project_id = request.query_params.get('project', None)
        self.queryset = self.serializer_class.setup_eager_loading(self.queryset)
        questions = QuestionnaireQuestion.objects.get_project_indicator_questions(project_id)
        self.queryset = self.queryset.filter(question__in=questions, is_appreciation_cause=False, coded_causes__isnull=True)
        return super(FrustrationWhyCauseViewSet, self).list(request, *args, **kwargs)


class AppreciationWhyCauseViewSet(ListModelMixin, viewsets.GenericViewSet):
    serializer_class = SimpleWhyCauseSerializer
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsTenantConsultant),)
    pagination_class = AppreciationWhyCausesPagination
    queryset = WhyCause.objects.all()

    def list(self, request, *args, **kwargs):
        project_id = request.query_params.get('project', None)
        self.queryset = self.serializer_class.setup_eager_loading(self.queryset)
        questions = QuestionnaireQuestion.objects.get_project_indicator_questions(project_id)
        self.queryset = self.queryset.filter(question__in=questions, is_appreciation_cause=True, coded_causes__isnull=True)
        return super(AppreciationWhyCauseViewSet, self).list(request, *args, **kwargs)


class WhyCauseViewSet(viewsets.ModelViewSet):
    """

    """
    queryset = WhyCause.objects.all()
    serializer_class = WhyCauseSerializer
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsTenantConsultant),)
    encode_serializer_class = QuestionWithWhyCausesSerializer

    @detail_route(['post'])
    def split(self, request, pk=None):
        why_cause = get_object_or_404(WhyCause, pk=pk)

        why_cause.update_answer(request.data.get('answer'))

        validated_coded_causes = self._check_if_coded_causes_exist(request.data.get('coded_causes'))
        # update them in case the why cause has been moved (on frontend) but no save has been issued.
        why_cause.update_coded_causes(validated_coded_causes)

        new_why_causes_answers = request.data.get('split_list', [])
        why_cause_to_serialize = why_cause.create_clones(new_why_causes_answers)

        serializer = WhyCauseSerializer(why_cause_to_serialize, many=True)
        return Response(serializer.data)

    @detail_route(['post'])
    def appreciation(self, request, pk=None):
        why_cause = get_object_or_404(WhyCause, pk=pk)
        why_cause.change_appreciation_cause()

        return Response(status=status.HTTP_200_OK)

    @staticmethod
    def _get_why_causes(project_id, data):
        why_causes_changes = {x['id']: x.get('coded_causes', []) for x in data}
        return WhyCause.objects.filter(pk__in=why_causes_changes.keys(),
                                       question__questionnaire__evaluation__project=project_id)

    @staticmethod
    def _check_if_coded_causes_exist(coded_cause_ids):
        validated_coded_causes_list = list()
        for id in coded_cause_ids:
            if CodedCause.objects.filter(pk=id).exists():
                validated_coded_causes_list.append(id)

        return validated_coded_causes_list
