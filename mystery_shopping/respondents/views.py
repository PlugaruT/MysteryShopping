import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_condition import Or
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from mystery_shopping.companies.models import CompanyElement
from mystery_shopping.mystery_shopping_utils.custom_filters import DetractorIndicatorMultipleChoiceFilter
from mystery_shopping.mystery_shopping_utils.paginators import DetractorRespondentPaginator
from mystery_shopping.mystery_shopping_utils.permissions import DetractorFilterPerCompanyElement
from mystery_shopping.questionnaires.models import Questionnaire
from mystery_shopping.questionnaires.serializers import DetractorRespondentForTenantSerializer, \
    DetractorRespondentForClientSerializer
from mystery_shopping.respondents.models import Respondent
from mystery_shopping.users.permissions import IsTenantConsultant
from mystery_shopping.users.permissions import IsTenantProductManager, HasReadOnlyAccessToProjectsOrEvaluations
from mystery_shopping.users.permissions import IsTenantProjectManager


class RespondentFilter(django_filters.rest_framework.FilterSet):
    places = django_filters.ModelMultipleChoiceFilter(queryset=CompanyElement.objects.all(),
                                                      name="evaluation__company_element")
    date = django_filters.DateFromToRangeFilter(name="evaluation__time_accomplished", lookup_expr='date')
    questions = django_filters.AllValuesMultipleFilter(name='number_of_questions')
    indicators = DetractorIndicatorMultipleChoiceFilter(name="evaluation__questionnaire__questions__additional_info",
                                                        conjoined=True,
                                                        query_manager=Questionnaire.objects.filter)

    class Meta:
        model = Respondent
        fields = ['date', 'places', 'status', 'questions', 'indicators']


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
