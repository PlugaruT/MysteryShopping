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

    def get_queryset(self):
        """
        Termprary solution.
        Filter dashboard according to project if 'project' query param is present
        :return:
        """
        queryset = self.queryset.all()
        project = self.request.query_params.get('project', None)

        if project:
            try:
                queryset = queryset.filter(project=project)
            except:
                queryset = None

        return queryset


class DashboardCommentViewSet(viewsets.ModelViewSet):
    queryset = DashboardComment.objects.all()
    serializer_class = DashboardCommentSerializer
