from collections import namedtuple

import django_filters
from django.shortcuts import get_object_or_404
from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_condition.permissions import C, ConditionalPermission

from rest_framework import viewsets
from rest_framework.decorators import list_route, detail_route
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_condition import Or

from mystery_shopping.companies.models import CompanyElement
from mystery_shopping.mystery_shopping_utils.models import TenantFilter
from mystery_shopping.mystery_shopping_utils.paginators import EvaluationPagination, ProjectStatisticsPaginator
from mystery_shopping.mystery_shopping_utils.views import GetSerializerClassMixin
from mystery_shopping.projects.constants import EvaluationStatus
from mystery_shopping.projects.mixins import EvaluationViewMixIn, UpdateSerializerMixin
from mystery_shopping.projects.serializers import ProjectSerializerGET, ResearchMethodologySerializerGET, \
    EvaluationSerializerGET, EvaluationAssessmentLevelSerializerGET, EvaluationAssessmentCommentSerializerGET, \
    ProjectStatisticsForTenantSerializerGET, ProjectStatisticsForCompanySerializerGET
from mystery_shopping.users.services import ShopperService
from .models import Project
from .models import ResearchMethodology
from .models import Evaluation
from .models import EvaluationAssessmentLevel
from .models import EvaluationAssessmentComment
from .serializers import ProjectSerializer
from .serializers import ResearchMethodologySerializer
from .serializers import EvaluationSerializer
from .serializers import EvaluationAssessmentLevelSerializer
from .serializers import EvaluationAssessmentCommentSerializer
from .serializers import ProjectStatisticsForCompanySerializer
from .serializers import ProjectStatisticsForTenantSerializer

from mystery_shopping.users.permissions import IsTenantProductManager, IsShopperAccountOwner
from mystery_shopping.users.permissions import HasReadOnlyAccessToProjectsOrEvaluations
from mystery_shopping.users.permissions import IsTenantProjectManager
from mystery_shopping.users.permissions import IsTenantConsultant
from mystery_shopping.users.permissions import IsShopper
from mystery_shopping.users.permissions import HasAccessToProjectsOrEvaluations


class ProjectViewSet(GetSerializerClassMixin, viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    serializer_class_get = ProjectSerializerGET
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager),)
    filter_backends = (TenantFilter,)

    def get_queryset(self):
        """Filter queryset based on Project type ('c' or by default 'm') and according
        to the Tenant the current user belongs to.
        """
        project_type = self.request.query_params.get('type', 'm')
        queryset = self.queryset.filter(type=project_type)
        return queryset

    # Todo: update this view
    @list_route(permission_classes=(IsAuthenticated, IsShopperAccountOwner), methods=['get'])
    def collectorevaluations(self, request):
        """A view to return a list of projects, which has places (entities or sections) paired up with their corresponding
        questionnaires.

        The view serves calls from Customer Experience Index project and returns the
        list of available entities with all the required information to fill in a
        questionnaire and create a realized evaluation.

        :returns: List of projects with place and questionnaire data.
        :rtype: list
        """
        if request.user.is_collector():
            shopper_service = ShopperService(request.user.shopper)
            available_list_of_places = shopper_service.get_available_list_of_places_with_questionnaires()
        else:
            available_list_of_places = list()

        return Response(available_list_of_places, status=status.HTTP_200_OK)


# Todo: try ModelViewSet
class ProjectPerCompanyViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [ConditionalPermission, IsAuthenticated]
    permission_condition = (C(HasAccessToProjectsOrEvaluations) | HasReadOnlyAccessToProjectsOrEvaluations)
    filter_backends = (TenantFilter, )

    def list(self, request, company_element_pk=None):
        project_type = self.request.query_params.get('type', 'm')
        queryset = self.filter_queryset(self.queryset)
        queryset = queryset.filter(company=company_element_pk, type=project_type)
        if self.request.user.user_type == 'tenantconsultant':
            queryset = self.queryset.filter(consultants__user=self.request.user)
        serializer = ProjectSerializerGET(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, pk=None, company_element_pk=None):
        serializer = ProjectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ProjectSerializerGET(serializer.instance).data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None, company_element_pk=None):
        queryset = self.queryset.filter(pk=pk, company=company_element_pk)
        project = get_object_or_404(queryset, pk=pk)
        self.check_object_permissions(request, project)
        serializer = ProjectSerializerGET(project)
        return Response(serializer.data)

    def update(self, request, pk=None, company_element_pk=None):
        request.data['research_methodology']['tenant'] = request.user.tenant.pk
        queryset = self.queryset.filter(pk=pk, company=company_element_pk)
        project = get_object_or_404(queryset, pk=pk)
        serializer = ProjectSerializer(project, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ProjectSerializerGET(serializer.instance).data)


class ResearchMethodologyViewSet(GetSerializerClassMixin, viewsets.ModelViewSet):
    queryset = ResearchMethodology.objects.all()
    serializer_class = ResearchMethodologySerializer
    serializer_class_get = ResearchMethodologySerializerGET
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager),)
    filter_backends = (TenantFilter,)


class EvaluationViewSet(UpdateSerializerMixin, EvaluationViewMixIn, viewsets.ModelViewSet):
    queryset = Evaluation.objects.all()
    serializer_class = EvaluationSerializer
    serializer_class_get = EvaluationSerializerGET
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsTenantConsultant, IsShopper),)
    pagination_class = EvaluationPagination

    def get_queryset(self):
        queryset = self.serializer_class.setup_eager_loading(self.queryset)
        if self.request.user.user_type in ['tenantproductmanager', 'tenantprojectmanager', 'tenantconsultant']:
            queryset = queryset.filter(project__tenant=self.request.user.tenant)
        elif self.request.user.user_type is 'shopper':
            queryset = queryset.filter(shopper__user=self.request.user)
        return queryset

    @detail_route(methods=['put'])
    def collect(self, request, pk=None):
        evaluation = get_object_or_404(Evaluation, pk=pk)
        self._serializer_update(evaluation, request.data)

        available_evaluation = self._check_if_available_evaluation(evaluation)

        response = dict()
        if available_evaluation.evaluation is not None:
            response['evaluation'] = self.serializer_class(available_evaluation.evaluation).data
            response['count'] = available_evaluation.count

        return Response(response)

    @staticmethod
    def _check_if_available_evaluation(evaluation):
        AvailableEvaluation = namedtuple('AvailableEvaluation', ['evaluation', 'count'])

        evaluations_to_collect = Evaluation.objects.filter(project=evaluation.project, shopper=evaluation.shopper,
                                                           status=EvaluationStatus.PLANNED,
                                                           entity=evaluation.entity, section=evaluation.section)

        return AvailableEvaluation(evaluation=evaluations_to_collect.first(),
                                   count=evaluations_to_collect.count())


class EvaluationPerShopperViewSet(viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated, HasAccessToProjectsOrEvaluations,)
    serializer_class = EvaluationSerializer
    filter_backends = (TenantFilter,)

    def list(self, request, shopper_pk=None):
        queryset = Evaluation.objects.filter(shopper=shopper_pk)
        queryset = self.filter_queryset(queryset)
        serializer = EvaluationSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None, shopper_pk=None):
        evaluation = get_object_or_404(Evaluation, pk=pk, shopper=shopper_pk)
        self.check_object_permissions(request, evaluation)
        serializer = EvaluationSerializer(evaluation)
        return Response(serializer.data)


class EvaluationsFilter(django_filters.rest_framework.FilterSet):
    date = django_filters.DateFromToRangeFilter(name="time_accomplished", lookup_expr='date')
    collector = django_filters.AllValuesMultipleFilter(name='shopper')

    class Meta:
        model = Evaluation
        fields = ['date', 'company_element', 'collector']


class EvaluationPerProjectViewSet(ListModelMixin, EvaluationViewMixIn, viewsets.GenericViewSet):
    serializer_class = EvaluationSerializerGET
    permission_classes = (IsAuthenticated, HasAccessToProjectsOrEvaluations,)
    pagination_class = EvaluationPagination
    filter_backends = (DjangoFilterBackend,)
    filter_class = EvaluationsFilter
    queryset = Evaluation.objects.all()

    def list(self, request, company_element_pk=None, project_pk=None):
        queryset = Evaluation.objects.get_project_evaluations(project=project_pk, company=company_element_pk)
        queryset = self.filter_queryset(queryset)
        queryset = self.serializer_class.setup_eager_loading(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = EvaluationSerializerGET(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None, company_element_pk=None, project_pk=None):
        evaluation = self._get_evaluation(pk, company_element_pk, project_pk)
        self.check_object_permissions(request, evaluation)
        serializer = EvaluationSerializerGET(evaluation)
        return Response(serializer.data)

    def update(self, request, pk=None, company_element_pk=None, project_pk=None):
        evaluation = self._get_evaluation(pk, company_element_pk, project_pk)
        serializer = EvaluationSerializer(evaluation, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, pk=None, company_element_pk=None, project_pk=None):
        evaluation = self._get_evaluation(pk, company_element_pk, project_pk)
        evaluation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def _get_evaluation(pk, company, project):
        queryset = Evaluation.objects.get_project_evaluations(project=project, company=company)
        return get_object_or_404(queryset, pk=pk)


class EvaluationAssessmentLevelViewSet(GetSerializerClassMixin,viewsets.ModelViewSet):
    queryset = EvaluationAssessmentLevel.objects.all()
    serializer_class = EvaluationAssessmentLevelSerializer
    serializer_class_get = EvaluationAssessmentLevelSerializerGET
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsTenantConsultant, IsShopper),)


class EvaluationAssessmentCommentViewSet(GetSerializerClassMixin, viewsets.ModelViewSet):
    queryset = EvaluationAssessmentComment.objects.all()
    serializer_class = EvaluationAssessmentCommentSerializer
    serializer_class_get = EvaluationAssessmentCommentSerializerGET
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsTenantConsultant, IsShopper),)


class ProjectStatisticsFilter(django_filters.rest_framework.FilterSet):
    places = django_filters.ModelMultipleChoiceFilter(queryset=CompanyElement.objects.all(), name="company_element")
    date = django_filters.DateFromToRangeFilter(name="time_accomplished", lookup_expr='date')
    collectors = django_filters.AllValuesMultipleFilter(name='shopper')

    class Meta:
        model = Evaluation
        fields = ['date', 'places', 'collectors']


class ProjectStatisticsForCompanyViewSet(GetSerializerClassMixin, viewsets.ModelViewSet):
    serializer_class = ProjectStatisticsForCompanySerializer
    serializer_class_get = ProjectStatisticsForCompanySerializerGET
    permission_classes = (IsAuthenticated, HasReadOnlyAccessToProjectsOrEvaluations,)
    pagination_class = ProjectStatisticsPaginator
    filter_backends = (DjangoFilterBackend,)
    filter_class = ProjectStatisticsFilter
    queryset = Evaluation.objects.all()

    def get_queryset(self):
        project = self.kwargs.get('project_pk', None)
        company_element = self.kwargs.get('company_element_pk', None)
        return Evaluation.objects.get_completed_project_evaluations(project=project, company=company_element)


class ProjectStatisticsForTenantViewSet(GetSerializerClassMixin, viewsets.ModelViewSet):
    serializer_class = ProjectStatisticsForTenantSerializer
    serializer_class_get = ProjectStatisticsForTenantSerializerGET
    permission_classes = (IsAuthenticated, HasAccessToProjectsOrEvaluations,)
    pagination_class = ProjectStatisticsPaginator
    filter_backends = (DjangoFilterBackend,)
    filter_class = ProjectStatisticsFilter
    queryset = Evaluation.objects.all()

    def get_queryset(self):
        project = self.kwargs.get('project_pk', None)
        company_element = self.kwargs.get('company_element_pk', None)
        return Evaluation.objects.get_completed_project_evaluations(project=project, company=company_element)
