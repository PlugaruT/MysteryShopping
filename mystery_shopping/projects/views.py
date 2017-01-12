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

from mystery_shopping.mystery_shopping_utils.models import TenantFilter
from mystery_shopping.mystery_shopping_utils.paginators import EvaluationPagination, ProjectStatisticsPaginator
from mystery_shopping.mystery_shopping_utils.views import GetSerializerClassMixin
from mystery_shopping.projects.constants import EvaluationStatus
from mystery_shopping.projects.mixins import EvaluationViewMixIn, UpdateSerializerMixin
from mystery_shopping.projects.serializers import ProjectStatisticsForTenantSerializerGET, \
    ProjectStatisticsForCompanySerializerGET
from mystery_shopping.users.services import ShopperService
from .models import PlaceToAssess
from .models import Project
from .models import ResearchMethodology
from .models import Evaluation
from .models import EvaluationAssessmentLevel
from .models import EvaluationAssessmentComment
from .serializers import PlaceToAssessSerializer
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


class PlaceToAssessViewSet(viewsets.ModelViewSet):
    queryset = PlaceToAssess.objects.all()
    serializer_class = PlaceToAssessSerializer
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager),)


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
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

    @detail_route(methods=['post'])
    def graph(self, request, pk=None):
        project = get_object_or_404(Project, pk=pk)
        project.save_graph_config(request.data)
        return Response(status=status.HTTP_200_OK)


class ProjectPerCompanyViewSet(viewsets.ViewSet):
    queryset = Project.objects.all()
    permission_classes = [ConditionalPermission, IsAuthenticated]
    permission_condition = (C(HasAccessToProjectsOrEvaluations) | HasReadOnlyAccessToProjectsOrEvaluations)

    # ToDo: trebuie să definim cum folosim filtrele per tenant aici
    def list(self, request, company_pk=None):
        project_type = self.request.query_params.get('type', 'm')
        queryset = self.queryset.filter(company=company_pk, type=project_type,
                                        tenant=self.request.user.tenant)
        if self.request.user.user_type == 'tenantconsultant':
            queryset = self.queryset.filter(consultants__user=self.request.user)
        serializer = ProjectSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, pk=None, company_pk=None):
        serializer = ProjectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None, company_pk=None):
        queryset = self.queryset.filter(pk=pk, company=company_pk)
        project = get_object_or_404(queryset, pk=pk)
        self.check_object_permissions(request, project)
        serializer = ProjectSerializer(project)
        return Response(serializer.data)

    def update(self, request, pk=None, company_pk=None):
        request.data['research_methodology']['tenant'] = request.user.tenant.pk
        queryset = self.queryset.filter(pk=pk, company=company_pk)
        evaluation = get_object_or_404(queryset, pk=pk)
        serializer = ProjectSerializer(evaluation, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @detail_route(methods=['post'])
    def graph(self, request, pk=None, company_pk=None):
        project = get_object_or_404(Project, pk=pk)
        project.save_graph_config(request.data)
        return Response(status=status.HTTP_200_OK)


class ResearchMethodologyViewSet(viewsets.ModelViewSet):
    queryset = ResearchMethodology.objects.all()
    serializer_class = ResearchMethodologySerializer
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager),)
    filter_backends = (TenantFilter,)


class EvaluationViewSet(UpdateSerializerMixin, EvaluationViewMixIn, viewsets.ModelViewSet):
    queryset = Evaluation.objects.all()
    serializer_class = EvaluationSerializer
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsTenantConsultant, IsShopper),)

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


class EvaluationPerShopperViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated, HasAccessToProjectsOrEvaluations,)

    # ToDo: trebuie să definim cum folosim filtrele per tenant aici
    def list(self, request, shopper_pk=None):
        queryset = Evaluation.objects.filter(shopper=shopper_pk)
        serializer = EvaluationSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None, shopper_pk=None):
        evaluation = get_object_or_404(Evaluation, pk=pk, shopper=shopper_pk)
        self.check_object_permissions(request, evaluation)
        serializer = EvaluationSerializer(evaluation)
        return Response(serializer.data)


class EvaluationPerProjectViewSet(ListModelMixin, EvaluationViewMixIn, viewsets.GenericViewSet):
    serializer_class = EvaluationSerializer
    permission_classes = (IsAuthenticated, HasAccessToProjectsOrEvaluations,)
    pagination_class = EvaluationPagination
    queryset = Evaluation.objects.all()

    # ToDo: trebuie să definim cum folosim filtrele per tenant aici
    def list(self, request, company_pk=None, project_pk=None):
        queryset = Evaluation.objects.get_project_evaluations(project=project_pk, company=company_pk)
        queryset = self.serializer_class.setup_eager_loading(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = EvaluationSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None, company_pk=None, project_pk=None):
        evaluation = self._get_evaluation(pk, company_pk, project_pk)
        self.check_object_permissions(request, evaluation)
        serializer = EvaluationSerializer(evaluation)
        return Response(serializer.data)

    def update(self, request, pk=None, company_pk=None, project_pk=None):
        evaluation = self._get_evaluation(pk, company_pk, project_pk)
        serializer = EvaluationSerializer(evaluation, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, pk=None, company_pk=None, project_pk=None):
        evaluation = self._get_evaluation(pk, company_pk, project_pk)
        evaluation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def _get_evaluation(pk, company, project):
        queryset = Evaluation.objects.get_project_evaluations(project=project, project__company=company)
        return get_object_or_404(queryset, pk=pk)


class EvaluationAssessmentLevelViewSet(viewsets.ModelViewSet):
    queryset = EvaluationAssessmentLevel.objects.all()
    serializer_class = EvaluationAssessmentLevelSerializer
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsTenantConsultant, IsShopper),)


class EvaluationAssessmentCommentViewSet(viewsets.ModelViewSet):
    queryset = EvaluationAssessmentComment.objects.all()
    serializer_class = EvaluationAssessmentCommentSerializer
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsTenantConsultant, IsShopper),)


class ProjectStatisticsFilter(django_filters.rest_framework.FilterSet):
    date = django_filters.DateFromToRangeFilter(name="time_accomplished", lookup_expr='date')
    collector = django_filters.AllValuesMultipleFilter(name='shopper')

    class Meta:
        model = Evaluation
        fields = ['date', 'company_element', 'collector']


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
        company = self.kwargs.get('company_pk', None)
        return Evaluation.objects.get_completed_project_evaluations(project=project, company=company)


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
        company = self.kwargs.get('company_pk', None)
        return Evaluation.objects.get_completed_project_evaluations(project=project, company=company)
