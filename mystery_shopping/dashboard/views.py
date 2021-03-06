from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_condition import Or

from django.utils import timezone

from mystery_shopping.dashboard.serializers import DashboardTemplateSerializerGET
from mystery_shopping.mystery_shopping_utils.models import TenantFilter
from mystery_shopping.users.permissions import HasAccessToDashboard
from .models import DashboardTemplate
from .models import DashboardComment
from .serializers import DashboardTemplateSerializer
from .serializers import DashboardCommentSerializer


class DashboardTemplateView(viewsets.ModelViewSet):
    """

    """
    queryset = DashboardTemplate.objects.all()
    serializer_class = DashboardTemplateSerializer
    serializer_class_get = DashboardTemplateSerializerGET
    permission_classes = (HasAccessToDashboard,)
    filter_backends = (TenantFilter,)

    def get_queryset(self):
        """
        Filter dashboard according to company if 'company' query param is present
        :return:
        """
        company = self.request.query_params.get('company', None)
        queryset = self.queryset.filter(company=company, is_published=True)
        if not self.request.user.is_tenant_manager():
            queryset = self.queryset.filter(company=company, users=self.request.user.id)
        return queryset

    def create(self, request, *args, **kwargs):
        request.data['modified_by'] = request.user.id
        request.data['modified_date'] = timezone.now()
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.modified_by = request.user
        instance.modified_date = timezone.now()
        serializer = self.serializer_class(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED, headers=headers)


class DashboardCommentViewSet(viewsets.ModelViewSet):
    queryset = DashboardComment.objects.all()
    serializer_class = DashboardCommentSerializer
