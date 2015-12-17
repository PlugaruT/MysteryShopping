from rest_framework import viewsets

from .models import Project
from .models import ResearchMethodology
from .serializers import ProjectSerializer
from .serializers import ResearchMethodologySerializer
from mystery_shopping.users.permissions import IsTenantProjectManager


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = (IsTenantProjectManager,)


class ResearchMethodologyViewSet(viewsets.ModelViewSet):
    queryset = ResearchMethodology.objects.all()
    serializer_class = ResearchMethodologySerializer
    permission_classes = (IsTenantProjectManager,)
