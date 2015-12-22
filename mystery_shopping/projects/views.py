from rest_framework import viewsets
from rest_condition import Or

from .models import Project
from .models import ResearchMethodology
from .models import PlannedEvaluation
from .serializers import ProjectSerializer
from .serializers import ResearchMethodologySerializer
from .serializers import PlannedEvaluationSerializer
from mystery_shopping.users.permissions import IsTenantProjectManager
from mystery_shopping.users.permissions import IsTenantConsultant


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = (IsTenantProjectManager,)


class ResearchMethodologyViewSet(viewsets.ModelViewSet):
    queryset = ResearchMethodology.objects.all()
    serializer_class = ResearchMethodologySerializer
    permission_classes = (IsTenantProjectManager,)

class PlannedEvaluationViewSet(viewsets.ModelViewSet):
    queryset = PlannedEvaluation.objects.all()
    serializer_class = PlannedEvaluationSerializer
    permission_classes = (Or(IsTenantProjectManager, IsTenantConsultant),)




