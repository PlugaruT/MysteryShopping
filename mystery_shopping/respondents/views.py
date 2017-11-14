from datetime import datetime

from django_filters.rest_framework import DjangoFilterBackend
from rest_condition import Or
from rest_framework import status, viewsets
from rest_framework.decorators import detail_route
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from mystery_shopping.mystery_shopping_utils.paginators import RespondentPaginator
from mystery_shopping.respondents.filters import RespondentFilter
from mystery_shopping.respondents.models import Respondent, RespondentCase
from mystery_shopping.respondents.serializers import RespondentSerializer
from mystery_shopping.users.models import User
from mystery_shopping.users.permissions import IsDetractorManager, IsTenantConsultant, IsTenantProductManager, \
    IsTenantProjectManager


class RespondentViewSet(viewsets.ModelViewSet):
    queryset = Respondent.objects.without_cases()
    filter_backends = (DjangoFilterBackend,)
    filter_class = RespondentFilter
    pagination_class = RespondentPaginator
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsTenantConsultant),)
    serializer_class = RespondentSerializer

    def get_queryset(self):
        project = self.request.query_params.get('project')
        queryset = self.queryset.filter(evaluation__project_id=project)
        return self.serializer_class.setup_eager_loading(queryset)


class RespondentWithCasesViewSet(RespondentViewSet):
    queryset = Respondent.objects.with_cases()
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsTenantConsultant, IsDetractorManager),)


class RespondentCaseViewSet(viewsets.ModelViewSet):
    serializer_class = RespondentCase
    queryset = RespondentCase.objects.all()
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsTenantConsultant, IsDetractorManager),)
    pagination_class = RespondentPaginator

    @detail_route(methods=['post'])
    def escalate(self, request, pk=None):
        case = get_object_or_404(RespondentCase, pk=pk)
        reason = request.data.get('reason')

        case.escalate(reason)
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

    @detail_route(methods=['post'], url_path='follow-up')
    def follow_up(self, request, pk=None):
        case = get_object_or_404(RespondentCase, pk=pk)
        follow_up = request.data.get('follow_up')
        tags = request.data.get('follow_up_tags')

        case.follow_up(follow_up=follow_up, follow_up_tags=tags)
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
