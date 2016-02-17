from django.shortcuts import get_object_or_404

from rest_framework import viewsets
from rest_framework.serializers import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_condition import Or

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

from mystery_shopping.users.permissions import IsTenantProductManager
from mystery_shopping.users.permissions import IsTenantProjectManager
from mystery_shopping.users.permissions import IsTenantConsultant
from mystery_shopping.users.permissions import IsShopper
from mystery_shopping.users.permissions import HasAccessToEvaluations


class PlaceToAssessViewSet(viewsets.ModelViewSet):
    queryset = PlaceToAssess.objects.all()
    serializer_class = PlaceToAssessSerializer
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager),)


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager),)

    def get_queryset(self):
        queryset = Project.objects.all()
        # queryset = self.get_serializer_class().setup_eager_loading(queryset)
        queryset = queryset.filter(tenant=self.request.user.user_type_attr.tenant)
        return queryset


class ProjectPerCompanyViewSet(viewsets.ViewSet):
    permission_classes = (HasAccessToEvaluations,)

    def list(self, request, company_pk=None):
        queryset = Project.objects.filter(company=company_pk)
        serializer = ProjectSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None, company_pk=None):
        project = get_object_or_404(Project, pk=pk, company=company_pk)
        self.check_object_permissions(request, project)
        serializer = ProjectSerializer(project)
        return Response(serializer.data)


class ResearchMethodologyViewSet(viewsets.ModelViewSet):
    queryset = ResearchMethodology.objects.all()
    serializer_class = ResearchMethodologySerializer
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager),)

    def get_queryset(self):
        queryset = ResearchMethodology.objects.all()
        queryset = queryset.filter(tenant=self.request.user.user_type_attr.tenant)
        return queryset


class EvaluationViewSet(viewsets.ModelViewSet):
    queryset = Evaluation.objects.all()
    serializer_class = EvaluationSerializer
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsTenantConsultant, IsShopper),)

    def get_queryset(self):
        if self.request.user.user_type in ['tenantproductmanager', 'tenantprojectmanager', 'tenantconsultant']:
            queryset = Evaluation.objects.all()
            queryset = queryset.filter(project__tenant=self.request.user.user_type_attr.tenant)
            return queryset
        elif self.request.user.user_type is 'shopper':
            queryset = Evaluation.objects.all()
            queryset = queryset.filter(shopper__user=self.request.user)
            return queryset
        return None

    def create(self, request, *args, **kwargs):
        is_many = True if isinstance(request.data, list) else False
        if is_many:
            evaluations_left = Project.objects.get(pk=request.data[0]['project']).research_methodology.number_of_evaluations - Evaluation.objects.filter(project=request.data[0]['project']).count()
            if evaluations_left >= len(request.data):
                serializer = self.get_serializer(data=request.data, many=True)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
            else:
                raise ValidationError('You are trying to create more evaluations than the amount left.')
        else:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


# class PlannedEvaluationPerShopperViewSet(viewsets.ViewSet):
#     permission_classes = (IsAuthenticated, HasAccessToEvaluations, )
#
#     def list(self, request, shopper_pk=None):
#         queryset = PlannedEvaluation.objects.filter(shopper=shopper_pk)
#         serializer = PlannedEvaluationSerializer(queryset, many=True)
#         return Response(serializer.data)
#
#     def retrieve(self, request, pk=None, shopper_pk=None):
#         planned_evaluation = get_object_or_404(PlannedEvaluation, pk=pk, shopper=shopper_pk)
#         self.check_object_permissions(request, planned_evaluation)
#         serializer = PlannedEvaluationSerializer(planned_evaluation)
#         return Response(serializer.data)


# class AccomplishedEvaluationPerShopperViewSet(viewsets.ViewSet):
#     permission_classes = (HasAccessToEvaluations,)
#
#     def list(self, request, shopper_pk=None):
#         queryset = AccomplishedEvaluation.objects.filter(shopper=shopper_pk)
#         serializer = AccomplishedEvaluationsSerializer(queryset, many=True)
#         return Response(serializer.data)
#
#     def retrieve(self, request, pk=None, shopper_pk=None):
#         accomplished_evaluation = get_object_or_404(AccomplishedEvaluation, pk=pk, shopper=shopper_pk)
#         self.check_object_permissions(request, accomplished_evaluation)
#         serializer = AccomplishedEvaluationsSerializer(accomplished_evaluation)
#         return Response(serializer.data)


class EvaluationAssessmentLevelViewSet(viewsets.ModelViewSet):
    queryset = EvaluationAssessmentLevel.objects.all()
    serializer_class = EvaluationAssessmentLevelSerializer
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsTenantConsultant, IsShopper),)


class EvaluationAssessmentCommentViewSet(viewsets.ModelViewSet):
    queryset = EvaluationAssessmentComment.objects.all()
    serializer_class = EvaluationAssessmentCommentSerializer
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsTenantConsultant, IsShopper),)
