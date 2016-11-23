from django.shortcuts import get_object_or_404

from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_condition import Or
from rest_condition import And

from mystery_shopping.projects.mixins import EvaluationViewMixIn
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

    def get_queryset(self):
        """Filter queryset based on Project type ('c' or by default 'm') and according
        to the Tenant the current user belongs to.
        """
        queryset = self.queryset.all()
        project_type = self.request.query_params.get('type', 'm')
        project_type = project_type[0] if isinstance(project_type, list) else project_type
        queryset = queryset.filter(type=project_type)
        queryset = queryset.filter(tenant=self.request.user.tenant)
        return queryset

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


class ProjectPerCompanyViewSet(viewsets.ViewSet):
    queryset = Project.objects.all()
    permission_classes = (And(IsAuthenticated, Or(HasAccessToProjectsOrEvaluations, HasReadOnlyAccessToProjectsOrEvaluations)),)

    def list(self, request, company_pk=None):
        project_type = self.request.query_params.get('type', 'm')
        project_type = project_type[0] if isinstance(project_type, list) else project_type
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


class ResearchMethodologyViewSet(viewsets.ModelViewSet):
    queryset = ResearchMethodology.objects.all()
    serializer_class = ResearchMethodologySerializer
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager),)

    def get_queryset(self):
        queryset = ResearchMethodology.objects.all()
        queryset = queryset.filter(tenant=self.request.user.tenant)
        return queryset


class EvaluationViewSet(EvaluationViewMixIn, viewsets.ModelViewSet):
    queryset = Evaluation.objects.all()
    serializer_class = EvaluationSerializer
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsTenantConsultant, IsShopper),)

    def get_queryset(self):
        queryset = Evaluation.objects.all()
        queryset = self.get_serializer_class().setup_eager_loading(queryset)
        if self.request.user.user_type in ['tenantproductmanager', 'tenantprojectmanager', 'tenantconsultant']:
            queryset = queryset.filter(project__tenant=self.request.user.tenant)
        elif self.request.user.user_type is 'shopper':
            queryset = queryset.filter(shopper__user=self.request.user)
        return queryset


class EvaluationPerShopperViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated, HasAccessToProjectsOrEvaluations,)

    def list(self, request, shopper_pk=None):
        queryset = Evaluation.objects.filter(shopper=shopper_pk)
        serializer = EvaluationSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None, shopper_pk=None):
        evaluation = get_object_or_404(Evaluation, pk=pk, shopper=shopper_pk)
        self.check_object_permissions(request, evaluation)
        serializer = EvaluationSerializer(evaluation)
        return Response(serializer.data)


class EvaluationPerProjectViewSet(EvaluationViewMixIn, viewsets.ViewSet):
    serializer_class = EvaluationSerializer
    permission_classes = (IsAuthenticated, HasAccessToProjectsOrEvaluations,)

    def list(self, request, company_pk=None, project_pk=None):
        queryset = Evaluation.objects.filter(project=project_pk, project__company=company_pk)
        queryset = self.serializer_class.setup_eager_loading(queryset)
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

    def _get_evaluation(self, pk, company, project):
        queryset = Evaluation.objects.filter(pk=pk, project=project, project__company=company)
        return get_object_or_404(queryset, pk=pk)


class EvaluationAssessmentLevelViewSet(viewsets.ModelViewSet):
    queryset = EvaluationAssessmentLevel.objects.all()
    serializer_class = EvaluationAssessmentLevelSerializer
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsTenantConsultant, IsShopper),)


class EvaluationAssessmentCommentViewSet(viewsets.ModelViewSet):
    queryset = EvaluationAssessmentComment.objects.all()
    serializer_class = EvaluationAssessmentCommentSerializer
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsTenantConsultant, IsShopper),)


class ProjectStatisticsForCompanyViewSet(viewsets.ViewSet):
    serializer_class = ProjectStatisticsForCompanySerializer
    permission_classes = (IsAuthenticated, HasReadOnlyAccessToProjectsOrEvaluations,)

    def list(self, request, company_pk=None, project_pk=None):
        for_assessment = request.query_params.get('forAssessment', None)
        queryset = Evaluation.objects.filter(project=project_pk, project__company=company_pk)
        if for_assessment:
            if request.user.user_type == 'tenantconsultant':
                queryset = queryset.filter(evaluation_assessment_level__consultants__in=[request.user.user_type_attr])
            elif request.user.user_type == 'tenantprojectmanager':
                queryset = queryset.filter(evaluation_assessment_level__project_manager=request.user.user_type_attr)
            else:
                queryset = Evaluation.objects.none()

        serializer = ProjectStatisticsForCompanySerializer(queryset, many=True)
        return Response(serializer.data)


class ProjectStatisticsForTenantViewSet(viewsets.ViewSet):
    serializer_class = ProjectStatisticsForTenantSerializer
    permission_classes = (IsAuthenticated, HasAccessToProjectsOrEvaluations,)

    def list(self, request, company_pk=None, project_pk=None):
        for_assessment = request.query_params.get('forAssessment', None)
        queryset = Evaluation.objects.filter(project=project_pk, project__company=company_pk)
        if for_assessment:
            if request.user.user_type == 'tenantconsultant':
                queryset = queryset.filter(evaluation_assessment_level__consultants__in=[request.user.user_type_attr])
            elif request.user.user_type == 'tenantprojectmanager':
                queryset = queryset.filter(evaluation_assessment_level__project_manager=request.user.user_type_attr)
            else:
                queryset = Evaluation.objects.none()

        serializer = ProjectStatisticsForTenantSerializer(queryset, many=True)
        return Response(serializer.data)
