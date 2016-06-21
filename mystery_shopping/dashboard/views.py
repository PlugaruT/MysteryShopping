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

    def list(self, request, *args, **kwargs):
        project = self.request.query_params.get('project', None)
        queryset = self.queryset

        if project:
            try:
                queryset = queryset.filter(project=project)
            except:
                queryset = None

        serializer = DashboardTemplateSerializer(queryset, many=True)
        return Response(serializer.data)




class DashboardCommentViewSet(viewsets.ModelViewSet):
    queryset = DashboardComment.objects.all()
    serializer_class = DashboardCommentSerializer
