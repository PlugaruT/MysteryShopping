from django_filters.rest_framework import DjangoFilterBackend
from rest_condition import Or
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from mystery_shopping.mystery_shopping_utils.paginators import DetractorRespondentPaginator
from mystery_shopping.mystery_shopping_utils.permissions import DetractorFilterPerCompanyElement
from mystery_shopping.questionnaires.serializers import DetractorRespondentForClientSerializer, \
    DetractorRespondentForTenantSerializer
from mystery_shopping.respondents.filters import RespondentFilter
from mystery_shopping.respondents.models import Respondent
from mystery_shopping.users.permissions import HasReadOnlyAccessToProjectsOrEvaluations, IsTenantConsultant, \
    IsTenantProductManager, IsTenantProjectManager


class RespondentForTenantViewSet(viewsets.ModelViewSet):
    queryset = Respondent.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filter_class = RespondentFilter
    pagination_class = DetractorRespondentPaginator
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsTenantConsultant),)
    serializer_class = DetractorRespondentForTenantSerializer

    def get_queryset(self):
        project = self.request.query_params.get('project')
        queryset = Respondent.objects.filter(evaluation__project=project)
        return self.serializer_class.setup_eager_loading(queryset)


class RespondentForClientViewSet(viewsets.ModelViewSet):
    serializer_class = DetractorRespondentForClientSerializer
    queryset = Respondent.objects.all()
    permission_classes = (IsAuthenticated, HasReadOnlyAccessToProjectsOrEvaluations)
    pagination_class = DetractorRespondentPaginator
    filter_backends = (DetractorFilterPerCompanyElement, DjangoFilterBackend,)
    filter_class = RespondentFilter

    def get_queryset(self):
        queryset = self.serializer_class.setup_eager_loading(self.queryset)
        project = self.request.query_params.get('project')
        return queryset.filter(evaluation__project=project)
