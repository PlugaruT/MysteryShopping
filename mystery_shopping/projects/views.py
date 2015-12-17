from rest_framework import viewsets

from .models import Project
from .serializers import ProjectSerializer
from mystery_shopping.users.permissions import IsTenantProjectManager


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    # permission_classes = (IsTenantProjectManager,)
