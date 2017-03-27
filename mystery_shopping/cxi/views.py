from django.db.models import Sum, IntegerField, Case, When

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
from mystery_shopping.mystery_shopping_utils.constants import COLORS_MAPPING
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
     View that returns data for bar chart for indicators grouped by project or indicator

    Query params:

     * `project`: **required**, list of project ids to aggregate data for
     * `grouped`: a string, can be True or False
    """

    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsCompanyProjectManager,
                             IsCompanyManager, IsCompanyEmployee),)

    def get(self, request, *args, **kwargs):
        grouped_by_indicator = request.query_params.get('grouped', None)
        project_ids = request.query_params.getlist('project', [])
        place = request.query_params.get('place', None)
        project_list = Project.objects.filter(id__in=project_ids)
        data_per_project = dict()
        for project in project_list:
            data_per_project[project.name] = collect_data_for_overview_dashboard(project, place)

        if grouped_by_indicator:
            response = self.build_data_grouped_by_indicator(data_per_project)
        else:
            response = self.build_data_grouped_by_project(data_per_project)
        return Response(response, status=status.HTTP_200_OK)

    def build_data_grouped_by_project(self, projects_overview_data):
        """
        Method for aggregating data to be displayed on the bar chart by project
        :param projects_overview_data: raw data from method collect_data_for_overview_dashboard
        :return: list of dicts
        """
        response = list()
        data_grouped_by_project = self.extract_indicator_scores_for_project(projects_overview_data)
        data_grouped_by_indicator = self.group_data_by_indicator(data_grouped_by_project)
        for indicator_name, projects in data_grouped_by_indicator.items():
            response.append({
                "key": indicator_name,
                "values": self.build_data_points_list(projects)
            })
        return response

    def build_data_grouped_by_indicator(self, projects_overview_data):
        """
        Method for aggregating data to be displayed on the bar chart grouped by indicator.
        :param projects_overview_data: raw data from method collect_data_for_overview_dashboard
        :return: list of dicts
        """
        response = list()
        indicators_per_project = self.extract_indicator_scores_for_project(projects_overview_data)
        for project_name, indicators in indicators_per_project.items():
            response.append({
                "key": project_name,
                "values": self.build_data_points_list(indicators)
            })
        return response

    def build_data_points_list(self, list_of_tuples):
        """
        Method for that will return a list of objects with keys x and y. Each object represents
        a bar on the chart
        :param list_of_tuples: list of tuples, each tuple is of the form (value_for_x_axis, value_for_y_axis)
        :return: list of dicts
        """
        response = list()
        for obj in list_of_tuples:
            response.append(self.build_data_point(obj[0], obj[1]))
        return response

    @staticmethod
    def group_data_by_indicator(data_grouped_by_project):
        """
        Method that will group overview data by indicator for a list of projects. Each key from returning dict
        is the indicator name and for each indicator the value is a list of tuples. Tuples are of the form
        (project_name, indicator_score)
        :param data_grouped_by_project: dict that has each key the name of the project and the value is a list of dicts
         of the form {"indicator_name" : indicator_score}
        :return: dict
        """
        response = dict()
        for project_name, indicators in data_grouped_by_project.items():
            for indicator in indicators:
                response.setdefault(indicator[0], []).append((project_name, indicator[1]))
        return response

    @staticmethod
    def build_data_point(x, y):
        """
        Method for constructing a data point. Each point represents a dict with x and y value.
        :param x: value for x axis
        :param y: value for y axis
        :return: dict
        """
        return {
            "x": x,
            "y": y
        }

    @staticmethod
    def extract_indicator_scores_for_project(raw_overview_data):
        """
        Method for extracting only indicator scores from overview data. The returning dict is of the form
        {
            "project_name": [{"indicator_name": indicator_score}, {"indicator_name": indicator_score}]
        }
        :param raw_overview_data: raw data from method collect_data_for_overview_dashboard
        :return: dict
        """
        response = dict()
        for project_name, overview_data in raw_overview_data.items():
            response[project_name] = list()
            for indicator_name, indicators_scores in overview_data['score']['indicators'].items():
                response[project_name].append(
                    (indicator_name, indicators_scores['indicator'])
                )
        return response


class RespondentsDistribution(views.APIView):
    """
    
    View that will return a the distribution of respondents for an indicator. 
    
     Query params:

     * `project`: **required**, id of the project to aggregate data for
     * `indicator`: **required**, indicator name for which to get questions
     * `company_element`: **required**, id of the company element for which to aggregate data
    
    The list of dicts has the form:
    ```
    [
        {
            key: 'CHART.DETRACTOR',
            value: 5,
            color: '#f44336'
        },
        {
            key: 'CHART.PASSIVE',
            value: 2,
            color: '#9E9E9E'
        },
        {
            key: 'CHART.PROMOTERS',
            value: 9,
            color: '#4CAF50'
        }
    ]
    ```
    """

    def get(self, request, *args, **kwargs):
        indicator_name = request.query_params.get('indicator', None)
        project_id = request.query_params.get('project', None)
        company_element_id = request.query_params.getlist('company_element', []) or None
        questions_list = QuestionnaireQuestion.objects.get_indicator_questions_for_company_elements(
            project=project_id, indicator=indicator_name, company_elements=company_element_id)

        if indicator_name == 'NPS':
            response = self.build_data_for_nps_indicator(questions_list)
        else:
            response = self.build_data_for_other_indicators(questions_list)

        return Response(response, status.HTTP_200_OK)

    def build_data_for_nps_indicator(self, questions_list):
        number_of_questions = questions_list.count()
        respondents_data = questions_list.aggregate(
            DETRACTOR=Sum(
                Case(
                    When(score__lte=6, then=1),
                    output_field=IntegerField()
                )
            ),
            PASSIVE=Sum(
                Case(
                    When(score=7, then=1),
                    When(score=8, then=1),
                    output_field=IntegerField()
                )
            ),
            PROMOTERS=Sum(
                Case(
                    When(score__gte=9, then=1),
                    output_field=IntegerField()
                )
            )
        )
        return self.build_data_points_list(respondents_data, number_of_questions)

    def build_data_for_other_indicators(self, questions_list):
        number_of_questions = questions_list.count()
        respondents_data = questions_list.aggregate(
            NEGATIVE=Sum(
                Case(
                    When(score__lte=6, then=1),
                    output_field=IntegerField()
                )
            ),
            NEUTRAL=Sum(
                Case(
                    When(score=7, then=1),
                    When(score=8, then=1),
                    output_field=IntegerField()
                )
            ),
            POSITIVE=Sum(
                Case(
                    When(score__gte=9, then=1),
                    output_field=IntegerField()
                )
            )
        )

        return self.build_data_points_list(respondents_data, number_of_questions)

    def build_data_points_list(self, data_dict, number_of_questions):
        """
        Method for building the final result
        :param data_dict: Contains number of respondents of each type, example:
            {
                'POSITIVE': 47, 
                'NEUTRAL': 51, 
                'NEGATIVE': 2
            }
        :param number_of_questions: Number of total questions, used for computing % for each type if respondent
        :return: list of dicts
        """
        response = []
        number_of_questions = number_of_questions if number_of_questions else 1
        for key, value in data_dict.items():
            key_name = 'CHART.{}'.format(key.upper())
            value = value if value else 0
            percentage = value / number_of_questions * 100
            response.append(self.build_data_point(key_name, percentage, COLORS_MAPPING[key]))
        return response

    @staticmethod
    def build_data_point(key, value, color):
        return {
            "key": key,
            "value": value,
            "color": color
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
        company_element_permissions = request.user.management_permissions()

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
            response = self.collect_data_for_indicator_dashboard(project, company_element_id, indicator_type,
                                                                 company_element_permissions)

            return Response(response, status.HTTP_200_OK)

        return Response({
            'detail': 'Project was not provided'
        }, status.HTTP_400_BAD_REQUEST)

    # @CacheResult(age=60 * 60 * 24) # 24h
    def collect_data_for_indicator_dashboard(self, project, company_element_id, indicator_type, company_element_permissions):
        return CollectDataForIndicatorDashboard(project, company_element_id,
                                                indicator_type, company_element_permissions).build_response()

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
