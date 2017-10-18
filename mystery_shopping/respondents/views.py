from django_filters.rest_framework import DjangoFilterBackend
from rest_condition import Or
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.permissions import IsAuthenticated

from mystery_shopping.mystery_shopping_utils.paginators import DetractorRespondentPaginator
from mystery_shopping.mystery_shopping_utils.permissions import DetractorFilterPerCompanyElement
from mystery_shopping.respondents.serializers import RespondentForClientSerializer, \
    RespondentForTenantSerializer
from mystery_shopping.respondents.filters import RespondentFilter
from mystery_shopping.respondents.models import Respondent, RespondentCase
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
    permission_classes = (IsAuthenticated, )
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
