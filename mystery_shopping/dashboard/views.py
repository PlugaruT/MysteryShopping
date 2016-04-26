from rest_framework import views
from rest_framework import viewsets
from rest_framework.response import Response

from .models import DashboardTemplate
from .models import DashboardComment
from .serializers import DashboardTemplateSerializer
from .serializers import DashboardCommentSerializer


class DashboardTemplateView(viewsets.ModelViewSet):
    """

    """
    queryset = DashboardTemplate.objects.all()
    serializer_class = DashboardTemplateSerializer



class DashboardCommentViewSet(viewsets.ModelViewSet):
    queryset = DashboardComment.objects.all()
    serializer_class = DashboardCommentSerializer
