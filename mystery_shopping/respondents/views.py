from datetime import datetime

from django_filters.rest_framework import DjangoFilterBackend
from rest_condition import Or
from rest_framework import status, viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from mystery_shopping.common.models import Tag
from mystery_shopping.mystery_shopping_utils.paginators import RespondentPaginator
from mystery_shopping.mystery_shopping_utils.utils import aggregate_respondents_distribution, build_data_point, \
    calculate_percentage
from mystery_shopping.projects.constants import RespondentType
from mystery_shopping.questionnaires.models import QuestionnaireQuestion
from mystery_shopping.respondents.constants import RESPONDENTS_MAPPING
from mystery_shopping.respondents.filters import RespondentFilter
from mystery_shopping.respondents.models import Respondent, RespondentCase
from mystery_shopping.respondents.serializers import RespondentSerializer
from mystery_shopping.users.models import User
from mystery_shopping.users.permissions import IsCompanyProjectManager, IsDetractorManager, IsTenantConsultant, \
    IsTenantProductManager, IsTenantProjectManager


class RespondentViewSet(viewsets.ModelViewSet):
    queryset = Respondent.objects.without_cases()
    filter_backends = (DjangoFilterBackend,)
    filter_class = RespondentFilter
    pagination_class = RespondentPaginator
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsTenantConsultant,
                             IsCompanyProjectManager, IsDetractorManager),)
    serializer_class = RespondentSerializer

    def get_queryset(self):
        project = self.request.query_params.get('project')
        queryset = self.queryset.filter(evaluation__project_id=project)
        return self.serializer_class.setup_eager_loading(queryset)

    @list_route(methods=['get'])
    def neutral(self, request):
        queryset = self.filter_queryset(self.get_queryset()).filter(
            evaluation__questionnaire__questions__score__in=[RespondentType.PASSIVE_LOW.value,
                                                             RespondentType.PASSIVE_HIGH.value])

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        response = self.serializer_class(queryset, many=True)

        return Response(data=response.data, status=status.HTTP_200_OK)


class RespondentWithCasesViewSet(RespondentViewSet):
    queryset = Respondent.objects.with_cases()
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsTenantConsultant, IsDetractorManager,
                             IsCompanyProjectManager),)


class RespondentCaseViewSet(viewsets.ModelViewSet):
    serializer_class = RespondentCase
    queryset = RespondentCase.objects.all()
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsTenantConsultant, IsDetractorManager,
                             IsCompanyProjectManager),)
    pagination_class = RespondentPaginator

    @detail_route(methods=['post'])
    def escalate(self, request, pk=None):
        case = get_object_or_404(RespondentCase, pk=pk)
        reason = request.data.get('reason')
        user = request.user

        case.escalate(reason, user)
        case.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @detail_route(methods=['post'], url_path='start-analysis')
    def start_analysis(self, request, pk=None):
        case = get_object_or_404(RespondentCase, pk=pk)

        case.start_analysis()
        case.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @detail_route(methods=['post'])
    def analyse(self, request, pk=None):
        case = get_object_or_404(RespondentCase, pk=pk)
        issue = request.data.get('issue')
        tags = request.data.get('issue_tags')

        case.analyse(issue=issue, issue_tags=tags)
        case.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @detail_route(methods=['post'])
    def implement(self, request, pk=None):
        case = get_object_or_404(RespondentCase, pk=pk)
        solution = request.data.get('solution')
        tags = request.data.get('solution_tags')
        user_id = request.data.get('follow_up_user', None)
        date = request.data.get('follow_up_date', None)

        user = User.objects.get(pk=user_id) if user_id else None
        date_object = datetime.strptime(date, '%d-%m-%Y') if date else None

        if (user is None) != (date_object is None):
            return Response(data=[{'details': 'You must provide values for both date and user, or none of them'}],
                            status=status.HTTP_400_BAD_REQUEST)

        case.implement(solution=solution, solution_tags=tags, follow_up_date=date_object, follow_up_user=user)
        case.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @detail_route(methods=['post'], url_path='start-follow-up')
    def start_follow_up(self, request, pk=None):
        case = get_object_or_404(RespondentCase, pk=pk)

        case.start_follow_up()
        case.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @detail_route(methods=['post'], url_path='follow-up')
    def follow_up(self, request, pk=None):
        case = get_object_or_404(RespondentCase, pk=pk)
        follow_up = request.data.get('follow_up')
        tags = request.data.get('follow_up_tags')

        case.do_follow_up(follow_up=follow_up, follow_up_tags=tags)
        case.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @detail_route(methods=['post'])
    def assign(self, request, pk=None):
        case = get_object_or_404(RespondentCase, pk=pk)
        user_id = request.data.get('user')
        to_user = User.objects.get(pk=int(user_id))
        comment = request.data.get('comment')
        comment_user = request.user

        case.assign(to=to_user, comment=comment, user=comment_user)
        case.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @detail_route(methods=['post'], permission_classes=[IsCompanyProjectManager])
    def reassign(self, request, pk=None):
        self.assign(request, pk)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @detail_route(methods=['post'])
    def close(self, request, pk=None):
        case = get_object_or_404(RespondentCase, pk=pk)
        reason = request.data.get('reason')
        user = request.user

        case.close(reason=reason, user=user)
        case.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @detail_route(methods=['post'], url_path='add-comment')
    def add_comment(self, request, pk=None):
        case = get_object_or_404(RespondentCase, pk=pk)
        comment = request.data.get('comment')
        user = request.user

        case.add_comment(comment, user)
        return Response(status=status.HTTP_204_NO_CONTENT)


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


class AverageTimePerState(APIView):
    """
        View class that computes average time a case spends in each state
    """

    def get(self, request, *args, **kwargs):
        response = list()
        project_id = request.query_params.get('project', None)
        cases_info = RespondentCase.objects.get_average_time_per_state(project_id=project_id)
        for case in cases_info:
            response.append(build_data_point(case.get('state'), case.get('avg_time')))
        return Response(response, status=status.HTTP_200_OK)
