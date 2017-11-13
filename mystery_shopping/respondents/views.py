from django_filters.rest_framework import DjangoFilterBackend
from rest_condition import Or
from rest_framework import viewsets, status
from rest_framework.decorators import detail_route
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from mystery_shopping.mystery_shopping_utils.paginators import RespondentPaginator
from mystery_shopping.respondents.filters import RespondentFilter
from mystery_shopping.respondents.models import Respondent, RespondentCase
from mystery_shopping.respondents.serializers import RespondentSerializer
from mystery_shopping.users.permissions import (IsTenantConsultant,
                                                IsTenantProductManager,
                                                IsTenantProjectManager,
                                                IsDetractorManager)


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
        reason = request.POST['reason']

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
    def analyze(self, request, pk=None):
        case = get_object_or_404(RespondentCase, pk=pk)
        issue = request.POST['issue']
        tags = request.POST['tags']

        case.analyse(issue=issue, issue_tags=tags)
        case.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @detail_route(methods=['post'])
    def implement(self, request, pk=None):
        respondent = get_object_or_404(RespondentCase, pk=pk)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @detail_route(methods=['post'], url_path='follow-up')
    def follow_up(self, request, pk=None):
        pass

    @detail_route(methods=['post'])
    def solve(self, request, pk=None):
        pass

    @detail_route(methods=['post'])
    def close(self, request, pk=None):
        pass
