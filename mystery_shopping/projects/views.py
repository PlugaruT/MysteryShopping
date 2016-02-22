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
    permission_classes = (HasAccessToEvaluations,)  # TODO check whether this permission is appropriate here (maybe it should be HasAccessToProjects ?

    def list(self, request, company_pk=None):
        queryset = Project.objects.filter(company=company_pk)
        serializer = ProjectSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None, company_pk=None):
        queryset = Project.objects.filter(pk=pk, company=company_pk)
        project = get_object_or_404(queryset, pk=pk)
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
        project_id = request.data[0]['project'] if is_many else request.data['project']
        total_number_of_evaluations = Project.objects.get(pk=project_id).research_methodology.number_of_evaluations
        current_number_of_evaluations = Evaluation.objects.filter(project=project_id).count()
        evaluations_left = total_number_of_evaluations - current_number_of_evaluations
        evaluations_to_create = len(request.data) if is_many else 1
        print(evaluations_left, evaluations_to_create)
        if evaluations_to_create > evaluations_left:
            raise ValidationError('Number of evaluations exceeded. Left: {}.'.format(evaluations_left))

        serializer = self.get_serializer(data=request.data, many=is_many)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class EvaluationPerShopperViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated, HasAccessToEvaluations, )

    def list(self, request, shopper_pk=None):
        queryset = Evaluation.objects.filter(shopper=shopper_pk)
        serializer = EvaluationSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None, shopper_pk=None):
        evaluation = get_object_or_404(Evaluation, pk=pk, shopper=shopper_pk)
        self.check_object_permissions(request, evaluation)
        serializer = EvaluationSerializer(evaluation)
        return Response(serializer.data)


class EvaluationPerProjectViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated, HasAccessToEvaluations, )
    serializer_class = EvaluationSerializer

    def get_serializer(self):
        return self.serializer_class

    def list(self, request, company_pk=None, project_pk=None):
        queryset = Evaluation.objects.filter(project=project_pk, project__company=company_pk)
        serializer = EvaluationSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None, company_pk=None, project_pk=None):
        queryset = Evaluation.objects.filter(pk=pk, project=project_pk, project__company=company_pk)
        evaluation = get_object_or_404(queryset, pk=pk)
        self.check_object_permissions(request, evaluation)
        serializer = EvaluationSerializer(evaluation)
        return Response(serializer.data)

    def update(self, request, pk=None, company_pk=None, project_pk=None):
        queryset = Evaluation.objects.filter(pk=pk, project=project_pk, project__company=company_pk)
        evaluation = get_object_or_404(queryset, pk=pk)
        serializer = EvaluationSerializer(evaluation, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, pk=None, company_pk=None, project_pk=None):
        queryset = Evaluation.objects.filter(pk=pk, project=project_pk, project__company=company_pk)
        evaluation = get_object_or_404(queryset, pk=pk)
        evaluation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EvaluationAssessmentLevelViewSet(viewsets.ModelViewSet):
    queryset = EvaluationAssessmentLevel.objects.all()
    serializer_class = EvaluationAssessmentLevelSerializer
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsTenantConsultant, IsShopper),)


class EvaluationAssessmentCommentViewSet(viewsets.ModelViewSet):
    queryset = EvaluationAssessmentComment.objects.all()
    serializer_class = EvaluationAssessmentCommentSerializer
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsTenantConsultant, IsShopper),)
