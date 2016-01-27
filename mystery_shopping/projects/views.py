from django.shortcuts import get_object_or_404

from rest_framework import viewsets
from rest_framework.response import Response
from rest_condition import Or

from .models import Project
from .models import ResearchMethodology
from .models import PlannedEvaluation
from .models import AccomplishedEvaluation
from .serializers import ProjectSerializer
from .serializers import ResearchMethodologySerializer
from .serializers import PlannedEvaluationSerializer
from .serializers import AccomplishedEvaluationsSerializer
from mystery_shopping.users.permissions import IsTenantProductManager
from mystery_shopping.users.permissions import IsTenantProjectManager
from mystery_shopping.users.permissions import IsTenantConsultant
from mystery_shopping.users.permissions import IsShopper
from mystery_shopping.users.permissions import HasAccessToEvaluations


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager),)


class ResearchMethodologyViewSet(viewsets.ModelViewSet):
    queryset = ResearchMethodology.objects.all()
    serializer_class = ResearchMethodologySerializer
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager),)


class PlannedEvaluationViewSet(viewsets.ModelViewSet):
    queryset = PlannedEvaluation.objects.all()
    serializer_class = PlannedEvaluationSerializer
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsTenantConsultant, IsShopper),)

    def get_queryset(self):
        if self.request.user.user_type in ['tenantproductmanager', 'tenantprojectmanager', 'tenantconsultant']:
            return PlannedEvaluation.objects.all()
        elif self.request.user.user_type is 'shopper':
            return PlannedEvaluation.objects.filter(shopper__user=self.request.user)
        return None


class PlannedEvaluationPerShopperViewSet(viewsets.ViewSet):
    permission_classes = (HasAccessToEvaluations,)

    def list(self, request, shopper_pk=None):
        queryset = PlannedEvaluation.objects.filter(shopper__user=shopper_pk)
        serializer = PlannedEvaluationSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None, shopper_pk=None):
        planned_evaluation = get_object_or_404(PlannedEvaluation, pk=pk, shopper=shopper_pk)
        self.check_object_permissions(request, planned_evaluation)
        serializer = PlannedEvaluationSerializer(planned_evaluation)
        return Response(serializer.data)


class AccomplishedEvaluationViewSet(viewsets.ModelViewSet):
    queryset = AccomplishedEvaluation.objects.all()
    serializer_class = AccomplishedEvaluationsSerializer
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsTenantConsultant, IsShopper),)

    def get_queryset(self):
        if self.request.user.user_type in ['tenantproductmanager', 'tenantprojectmanager', 'tenantconsultant']:
            return AccomplishedEvaluation.objects.all()
        elif self.request.user.user_type is 'shopper':
            return AccomplishedEvaluation.objects.filter(shopper__user=self.request.user)
        return None

class AccomplishedEvaluationPerShopperViewSet(viewsets.ViewSet):
    permission_classes = (HasAccessToEvaluations,)

    def list(self, request, shopper_pk=None):
        queryset = AccomplishedEvaluation.objects.filter(shopper__user=shopper_pk)
        serializer = AccomplishedEvaluationsSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None, shopper_pk=None):
        accomplished_evaluation = get_object_or_404(AccomplishedEvaluation, pk=pk, shopper=shopper_pk)
        self.check_object_permissions(request, accomplished_evaluation)
        serializer = AccomplishedEvaluationsSerializer(accomplished_evaluation)
        return Response(serializer.data)
