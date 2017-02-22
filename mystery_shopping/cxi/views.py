from django.shortcuts import get_object_or_404
from guardian.shortcuts import get_objects_for_user
from rest_condition import Or
from rest_framework import status
from rest_framework import views
from rest_framework import viewsets
from rest_framework.decorators import list_route, detail_route
from rest_framework.filters import SearchFilter
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response

from mystery_shopping.companies.models import Company, CompanyElement
from mystery_shopping.cxi.algorithms import GetPerDayQuestionnaireData
from mystery_shopping.cxi.serializers import SimpleWhyCauseSerializer
from mystery_shopping.mystery_shopping_utils.models import TenantFilter
from mystery_shopping.mystery_shopping_utils.paginators import FrustrationWhyCausesPagination, \
    AppreciationWhyCausesPagination, WhyCausesPagination
from mystery_shopping.projects.models import Project
from mystery_shopping.questionnaires.models import QuestionnaireQuestion
from mystery_shopping.questionnaires.utils import check_interval_date
from mystery_shopping.users.models import ClientManager
from mystery_shopping.users.permissions import IsCompanyManager, IsCompanyEmployee
from mystery_shopping.users.permissions import IsCompanyProjectManager
from mystery_shopping.users.permissions import IsTenantConsultant
from mystery_shopping.users.permissions import IsTenantProductManager
from mystery_shopping.users.permissions import IsTenantProjectManager
from .algorithms import CodedCausesPercentageTable
from .algorithms import CollectDataForIndicatorDashboard
from .algorithms import collect_data_for_overview_dashboard
from .algorithms import get_company_indicator_questions_list
from .algorithms import get_project_indicator_questions_list
from .models import CodedCause
from .models import CodedCauseLabel
from .models import ProjectComment
from .models import WhyCause
from .serializers import CodedCauseLabelSerializer
from .serializers import CodedCauseSerializer
from .serializers import ProjectCommentSerializer
from .serializers import WhyCauseSerializer


class ClearCodedCauseMixin:
    @staticmethod
    def clear_coded_cause(why_causes):
        for why_cause in why_causes:
            why_cause.coded_causes.clear()


class CodedCauseLabelViewSet(viewsets.ModelViewSet):
    queryset = CodedCauseLabel.objects.all()
    serializer_class = CodedCauseLabelSerializer


class CodedCauseViewSet(ClearCodedCauseMixin, viewsets.ModelViewSet):
    queryset = CodedCause.objects.all()
    queryset = CodedCauseSerializer().setup_eager_loading(queryset)
    serializer_class = CodedCauseSerializer
    filter_backends = (TenantFilter,)

    def get_queryset(self):
        project_id = self.request.query_params.get('project')
        if project_id:
            try:
                project = Project.objects.get(pk=project_id)
                return self.queryset.filter(project=project)
            except (Project.DoesNotExist, ValueError):
                self.queryset.none()
        return self.queryset.none()

    def create(self, request, *args, **kwargs):
        # add tenant from the request.user to the request.data that is sent to the Coded CauseSerializer
        request.data['tenant'] = request.user.tenant.id
        request.data['coded_label']['tenant'] = request.user.tenant.id
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @detail_route(methods=['put'], url_path='save-why-cause')
    def save_why_cause(self, request, pk=None):
        coded_cause = get_object_or_404(CodedCause, pk=pk)
        why_causes = WhyCause.objects.filter(id__in=request.data)
        questions_from_why_causes = list(why_causes.values_list('question', flat=True))
        questions_from_coded_cause = list(coded_cause.raw_causes.values_list('question', flat=True))
        dup_questions_from_why_causes = set(
            question for question in questions_from_why_causes if questions_from_why_causes.count(question) > 1)

        all_questions = list(dup_questions_from_why_causes) + questions_from_coded_cause
        why_causes = why_causes.exclude(question__in=all_questions)
        self.clear_coded_cause(why_causes)
        coded_cause.raw_causes.add(*list(why_causes))
        return Response(status=status.HTTP_202_ACCEPTED)

    @staticmethod
    def get_common_question(why_causes, coded_cause):
        questions_from_coded_cause = coded_cause.raw_causes.values_list('question', flat=True)
        questions_from_why_causes = why_causes.values_list('question', flat=True)
        return list(set(questions_from_coded_cause).intersection(questions_from_why_causes))

    @list_route(methods=['get'])
    def sorted(self, request):
        indicator = self.request.query_params.get('type')
        queryset = self.filter_queryset(self.get_queryset().filter(type=indicator))
        serializer = self.serializer_class(queryset, many=True)
        response = self.group_by_sentiment(serializer.data)
        return Response(response)

    @staticmethod
    def group_by_sentiment(coded_causes):
        result = dict()
        for coded_cause in coded_causes:
            result.setdefault(coded_cause['sentiment'], []).append(coded_cause)
        return result


class ProjectCommentViewSet(viewsets.ModelViewSet):
    queryset = ProjectComment.objects.all()
    serializer_class = ProjectCommentSerializer


class CxiIndicatorTimeLapse(views.APIView):
    """
    View that returns collected data and results divided per day
    in a given time period.
    """

    def get(self, request, *args, **kwargs):
        company_id = request.query_params.get('company')
        start, end = check_interval_date(request.query_params)
        response = GetPerDayQuestionnaireData(start, end, company_id).build_response()
        return Response(response, status.HTTP_200_OK)


class BarChartGraph(views.APIView):
    """
    View that will return data for barchart
    """

    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsCompanyProjectManager,
                             IsCompanyManager, IsCompanyEmployee),)

    def get(self, request, *args, **kwargs):
        grouped_by = request.query_params.get('grouped', 'project')
        company = request.query_params.get('company', None)
        project_list = Project.objects.filter(company=company)
        response = [
            {
                "key": 'NPS',
                "color": '#bcbd22',
                "values": [
                    {
                        "x": 'Project 1',
                        "y": 10
                    },
                    {
                        "x": 'Project 2',
                        "y": 11
                    }
                    , {
                        "x": 'Project 3',
                        "y": 12
                    }
                ]
            },
            {
                "key": 'Placere',
                "color": '#1f77b4',
                "values": [
                    {
                        "x": 'Project 1',
                        "y": 14
                    },
                    {
                        "x": 'Project 2',
                        "y": 15
                    }
                    , {
                        "x": 'Project 3',
                        "y": 16
                    }
                ]
            },
            {
                "key": 'Utilitate',
                "color": 'pink',
                "values": [
                    {
                        "x": 'Project 1',
                        "y": 17
                    },
                    {
                        "x": 'Project 2',
                        "y": 18
                    }
                    , {
                        "x": 'Project 3',
                        "y": 19
                    }
                ]
            },
            {
                "key": 'Efort',
                "color": 'green',
                "values": [
                    {
                        "x": 'Project 1',
                        "y": 17
                    },
                    {
                        "x": 'Project 2',
                        "y": 35.5
                    }
                    , {
                        "x": 'Project 3',
                        "y": 19
                    }
                ]
            }]
        return Response(response, status=status.HTTP_200_OK)




    def build_indicator_data(self, indicator_name, indicator_data, color):
        values = list()
        for project_name, indicator_score in indicator_data.items():
            values.append(self.build_data_point(project_name, indicator_score))
        return {
            "key": indicator_name,
            "values": values,
            "color": color
        }

    @staticmethod
    def build_data_point(x, y):
        return {
            "x": x,
            "y": y
        }


class OverviewDashboard(views.APIView):
    """
    View that returns overview information per each indicator for department, entity or section

    Query params:

     * `project`: **required**, project id for filtering evaluations
     * `department`: department id
     * `entity`: entity id
     * `section`: section id
    """

    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsCompanyProjectManager,
                             IsCompanyManager, IsCompanyEmployee),)

    def get(self, request, *args, **kwargs):
        project_id = request.query_params.get('project', None)
        company_element_id = request.query_params.get('company_element', None)

        parameters_are_valid = self.parameter_is_valid(company_element_id)

        if project_id:
            if parameters_are_valid:
                return Response({
                    'detail': 'Entity param is invalid'
                }, status.HTTP_400_BAD_REQUEST)
            try:
                project = Project.objects.select_related('tenant').get(pk=project_id)
                if request.user.tenant != project.tenant:
                    return Response({'detail': 'You do not have permission to access to this project.'},
                                    status.HTTP_403_FORBIDDEN)

                response = collect_data_for_overview_dashboard(project, company_element_id)

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

    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsCompanyProjectManager,
                             IsCompanyManager, IsCompanyEmployee),)

    def get(self, request, *args, **kwargs):
        project_id = request.query_params.get('project', None)
        company_id = request.query_params.get('company', None)
        company_element_id = request.query_params.get('company_element', None)
        indicator_type = request.query_params.get('indicator', None)
        project = None

        parameters_are_valid = self.parameter_is_valid(company_element_id)

        if project_id is None:
            if request.user.is_client_user():
                company = request.user.user_company()
                project = Project.objects.get_latest_project_for_client_user(tenant=request.user.tenant,
                                                                             company=company)
            elif request.user.is_tenant_user() and company_id is not None:
                project = Project.objects.get_latest_project_for_client_user(tenant=request.user.tenant,
                                                                             company=company_id)
        elif project_id:
            # TODO: handle this in a more elegant way
            if parameters_are_valid:
                return Response({
                    'detail': 'Entity param is invalid'
                }, status.HTTP_400_BAD_REQUEST)
            try:
                project = Project.objects.select_related('tenant').get(pk=project_id)
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
            response = self.collect_data_for_indicator_dashboard(project, company_element_id, indicator_type)

            return Response(response, status.HTTP_200_OK)

        return Response({
            'detail': 'Project was not provided'
        }, status.HTTP_400_BAD_REQUEST)

    # @CacheResult(age=60 * 60 * 24) # 24h
    def collect_data_for_indicator_dashboard(self, project, company_element_id, indicator_type):
        return CollectDataForIndicatorDashboard(project, company_element_id,
                                                indicator_type).build_response()

    @staticmethod
    def parameter_is_valid(parameter):
        return parameter is not None and not parameter.isdigit()


class IndicatorDashboardList(views.APIView):
    """

    """

    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsCompanyProjectManager,
                             IsCompanyManager),)

    def get(self, request, *args, **kwargs):
        project_id = request.query_params.get('project', None)
        company_id = request.query_params.get('company', None)

        # Since the company parameter "incapsulates" the project one
        # it would be better to check for it first
        if company_id:
            try:
                company = Company.objects.get(pk=company_id)
            except (Company.DoesNotExist, ValueError):
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
    View for calculating percentage for each coded cause.

    Query params:

    * `indicator`: **required**, name of the indicator to filter coded causes.
    * `project`: **required**, project id to filter coded causes.
    """
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsCompanyProjectManager, IsCompanyManager,
                             IsTenantConsultant),)

    def get(self, request, *args, **kwargs):
        indicator = request.query_params.get('indicator')
        project_id = request.query_params.get('project')
        list_of_places = get_objects_for_user(request.user, klass=CompanyElement,
                                              perms=['view_coded_causes_for_companyelement']).values_list('id',
                                                                                                          flat=True)
        pre_response = self._pre_process_request(project_id, request.user)
        if pre_response:
            return Response(**pre_response)
        indicator_questions = QuestionnaireQuestion.objects.get_indicator_questions_for_company_elements(project_id,
                                                                                                         indicator,
                                                                                                         list_of_places)

        coded_cause_percentage = CodedCausesPercentageTable(indicator_questions)
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
                        status=status.HTTP_403_FORBIDDEN)

        return False


class FrustrationWhyCauseViewSet(ListModelMixin, viewsets.GenericViewSet):
    """
    View for listing all frustration Why Causes for a specific indicator. Response is paginated.

    Query params:

     * `project`: **required**, project id for filtering why causes
     * `type`: **required**, indicator name to filter by
     * `search`: search string used for search, it will do a case-insensitive partial match for field `answer`
    """
    serializer_class = SimpleWhyCauseSerializer
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsTenantConsultant),)
    pagination_class = FrustrationWhyCausesPagination
    filter_backends = (SearchFilter,)
    search_fields = ('answer',)
    queryset = WhyCause.objects.all()

    def get_queryset(self):
        return self.serializer_class.setup_eager_loading(self.queryset)

    def list(self, request, *args, **kwargs):
        project_id = request.query_params.get('project', None)
        indicator = request.query_params.get('type', None)
        questions = QuestionnaireQuestion.objects.get_project_indicator_questions(project_id)
        self.queryset = self.queryset.filter(question__in=questions, is_appreciation_cause=False,
                                             coded_causes__isnull=True, question__additional_info=indicator)
        return super(FrustrationWhyCauseViewSet, self).list(request, *args, **kwargs)


class AppreciationWhyCauseViewSet(ListModelMixin, viewsets.GenericViewSet):
    """
    View for listing all appreciation Why Causes for a specific indicator. Response is paginated.

    Query params:

     * `project`: **required**, project id for filtering why causes
     * `type`: **required**, indicator name to filter by
     * `search`: search string used for search, it will do a case-insensitive partial match for field `answer`
    """
    serializer_class = SimpleWhyCauseSerializer
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsTenantConsultant),)
    pagination_class = AppreciationWhyCausesPagination
    filter_backends = (SearchFilter,)
    search_fields = ('answer',)
    queryset = WhyCause.objects.all()

    def get_queryset(self):
        return self.serializer_class.setup_eager_loading(self.queryset)

    def list(self, request, *args, **kwargs):
        project_id = request.query_params.get('project', None)
        indicator = request.query_params.get('type', None)
        questions = QuestionnaireQuestion.objects.get_project_indicator_questions(project_id)
        self.queryset = self.queryset.filter(question__in=questions, is_appreciation_cause=True,
                                             coded_causes__isnull=True, question__additional_info=indicator)
        return super(AppreciationWhyCauseViewSet, self).list(request, *args, **kwargs)


class WhyCauseViewSet(ClearCodedCauseMixin, viewsets.ModelViewSet):
    """

    """
    queryset = WhyCause.objects.all()
    serializer_class = WhyCauseSerializer
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsTenantConsultant),)
    pagination_class = WhyCausesPagination

    def get_queryset(self):
        return self.serializer_class.setup_eager_loading(self.queryset)

    def list(self, request, *args, **kwargs):
        coded_cause_id = request.query_params.get('cause', None)
        queryset = self.queryset.filter(coded_causes=coded_cause_id)
        serializer = self.serializer_class(queryset, many=True)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @list_route(['put'], url_path='clear')
    def clear(self, request):
        """
        Endpoint for removing relation between why causes and coded cause. The request should contain list of id's of why causes
        :param request: request info, request.data contains list of id's
        :return: status code
        """
        why_causes = WhyCause.objects.filter(id__in=request.data)
        self.clear_coded_cause(why_causes)
        return Response(status=status.HTTP_202_ACCEPTED)

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
    def _check_if_coded_causes_exist(coded_cause_ids):
        validated_coded_causes_list = list()
        for id in coded_cause_ids:
            if CodedCause.objects.filter(pk=id).exists():
                validated_coded_causes_list.append(id)

        return validated_coded_causes_list
