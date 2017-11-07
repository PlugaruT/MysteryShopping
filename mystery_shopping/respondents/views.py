from django_filters.rest_framework import DjangoFilterBackend
from rest_condition import Or
from rest_framework import status, viewsets
from rest_framework.decorators import detail_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from mystery_shopping.common.models import Tag
from mystery_shopping.mystery_shopping_utils.paginators import DetractorRespondentPaginator
from mystery_shopping.mystery_shopping_utils.permissions import DetractorFilterPerCompanyElement
from mystery_shopping.mystery_shopping_utils.utils import aggregate_respondents_distribution, build_data_point, \
    calculate_percentage
from mystery_shopping.questionnaires.models import QuestionnaireQuestion
from mystery_shopping.respondents.constants import RESPONDENTS_MAPPING
from mystery_shopping.respondents.filters import RespondentFilter
from mystery_shopping.respondents.models import Respondent, RespondentCase
from mystery_shopping.respondents.serializers import RespondentForClientSerializer, \
    RespondentForTenantSerializer
from mystery_shopping.users.models import User
from mystery_shopping.users.permissions import HasReadOnlyAccessToProjectsOrEvaluations, IsTenantConsultant, \
    IsTenantProductManager, IsTenantProjectManager


class RespondentForTenantViewSet(viewsets.ModelViewSet):
    queryset = Respondent.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filter_class = RespondentFilter
    pagination_class = DetractorRespondentPaginator
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsTenantConsultant),)
    serializer_class = RespondentForTenantSerializer

    def get_queryset(self):
        project = self.request.query_params.get('project')
        queryset = Respondent.objects.filter(evaluation__project=project)
        return self.serializer_class.setup_eager_loading(queryset)


class RespondentForClientViewSet(viewsets.ModelViewSet):
    serializer_class = RespondentForClientSerializer
    queryset = Respondent.objects.all()
    permission_classes = (IsAuthenticated, HasReadOnlyAccessToProjectsOrEvaluations)
    pagination_class = DetractorRespondentPaginator
    filter_backends = (DetractorFilterPerCompanyElement, DjangoFilterBackend,)
    filter_class = RespondentFilter

    def get_queryset(self):
        queryset = self.serializer_class.setup_eager_loading(self.queryset)
        project = self.request.query_params.get('project')
        return queryset.filter(evaluation__project=project)


class RespondentCaseViewSet(viewsets.ModelViewSet):
    serializer_class = RespondentCase
    queryset = RespondentCase.objects.all()
    permission_classes = (IsAuthenticated,)
    pagination_class = DetractorRespondentPaginator

    @detail_route(methods=['post'])
    def escalate(self, request, pk=None):
        pass

    @detail_route(methods=['post'])
    def analyze(self, request, pk=None):
        pass

    @detail_route(methods=['post'])
    def implement(self, request, pk=None):
        pass

    @detail_route(methods=['post'], url_path='follow-up')
    def follow_up(self, request, pk=None):
        pass

    @detail_route(methods=['post'])
    def solve(self, request, pk=None):
        pass

    @detail_route(methods=['post'])
    def close(self, request, pk=None):
        pass


class RespondentsDistribution(APIView):
    """

    View that will return the distribution of respondents for an indicator.

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
        },
        {
            key: 'CHART.PASSIVE',
            value: 2,
        },
        {
            key: 'CHART.PROMOTERS',
            value: 9,
        }
    ]
    ```
    """

    NPS = 'NPS'

    def get(self, request, *args, **kwargs):
        indicator_name = request.query_params.get('indicator', None)
        project_id = request.query_params.get('project', None)
        company_element_id = request.query_params.getlist('company_element', [])
        questions_list = QuestionnaireQuestion.objects.get_indicator_questions_for_company_elements(
            project=project_id, indicator=indicator_name, company_elements=company_element_id)

        response = self.build_response_for_indicator(questions_list, indicator_name)

        return Response(response, status.HTTP_200_OK)

    def build_response_for_indicator(self, questions_list, indicator_name):
        number_of_questions = questions_list.count()
        respondents_data = aggregate_respondents_distribution(questions_list)
        if indicator_name != self.NPS:
            respondents_data = self.change_dict_keys(respondents_data)
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
        for key, value in data_dict.items():
            value = value if value else 0
            percentage = calculate_percentage(value, number_of_questions)
            response.append(self.build_data_point(key.upper(), percentage, value))
        return response

    @staticmethod
    def build_data_point(key, value, additional):
        return {
            "key": key,
            "value": value,
            "additional": additional
        }

    @staticmethod
    def change_dict_keys(dict_to_change):
        return dict((RESPONDENTS_MAPPING[key], value) for (key, value) in dict_to_change.items())


class RespondentCasesPerState(APIView):
    """
        View class that returns the number of cases for each possible state
    """

    def get(self, request, *args, **kwargs):
        response = list()
        project_id = request.query_params.get('project', None)
        cases_info = RespondentCase.objects.get_cases_per_state(project_id=project_id)
        for case in cases_info:
            response.append(build_data_point(case.get('state'), case.get('count')))

        return Response(response, status=status.HTTP_200_OK)


class RespondentCasesPerSolutionTag(APIView):
    """
        View class that returns the number of cases for each solution tag
    """

    def get(self, request, *args, **kwargs):
        response = list()
        project_id = request.query_params.get('project', None)
        tags_info = Tag.objects.get_solution_tags_info(project_id=project_id)
        for tag_info in tags_info:
            response.append(build_data_point(tag_info.get('name'), tag_info.get('count_cases')))
        return Response(response, status=status.HTTP_200_OK)


class RespondentCasesPerIssueTag(APIView):
    """
        View class that returns the number of cases for each issue tag

    """

    def get(self, request, *args, **kwargs):
        response = list()
        project_id = request.query_params.get('project', None)
        tags_info = Tag.objects.get_issue_tags_info(project_id=project_id)
        for tag_info in tags_info:
            response.append(build_data_point(tag_info.get('name'), tag_info.get('count_cases')))
        return Response(response, status=status.HTTP_200_OK)


class RespondentCasesPerUser(APIView):
    """
        View class that returns number of cases for each user
    """

    def get(self, request, *args, **kwargs):
        response = list()
        project_id = request.query_params.get('project', None)
        users_info = User.objects.get_cases_info(project_id=project_id)
        for user_info in users_info:
            key = '{} {}'.format(user_info.get('first_name'), user_info.get('last_name'))
            response.append(build_data_point(key, user_info.get('count_cases')))
        return Response(response, status=status.HTTP_200_OK)
