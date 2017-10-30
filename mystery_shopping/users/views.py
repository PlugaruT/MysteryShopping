# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.contrib.auth.models import Group, Permission
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_condition import Or
from rest_framework import status, viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from mystery_shopping.companies.models import CompanyElement
from mystery_shopping.companies.serializers import CompanyElementSerializer
from mystery_shopping.companies.utils import FilterCompanyStructure
from mystery_shopping.mystery_shopping_utils.models import TenantFilter
from mystery_shopping.mystery_shopping_utils.paginators import DetractorRespondentPaginator
from mystery_shopping.mystery_shopping_utils.permissions import DetractorFilterPerCompanyElement
from mystery_shopping.mystery_shopping_utils.views import GetSerializerClassMixin
from mystery_shopping.questionnaires.serializers import DetractorRespondentForClientSerializer, \
    DetractorRespondentForTenantSerializer
from mystery_shopping.users.filters import ClientFilter, DetractorFilter, ShopperFilter, UserFilter
from mystery_shopping.users.mixins import CreateUserMixin, DestroyOneToOneUserMixin
from mystery_shopping.users.models import ClientUser, Collector, DetractorRespondent, Shopper, User
from mystery_shopping.users.permissions import HasReadOnlyAccessToProjectsOrEvaluations, IsTenantConsultant, \
    IsTenantProductManager, IsTenantProjectManager
from mystery_shopping.users.roles import UserRole
from mystery_shopping.users.serializers import ClientUserSerializer, ClientUserSerializerGET, CollectorSerializer, \
    GroupSerializer, PermissionSerializer, ShopperSerializer, ShopperSerializerGET, UserSerializer, UserSerializerGET


class UserViewSet(GetSerializerClassMixin, viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    serializer_class_get = UserSerializerGET
    filter_backends = (TenantFilter, DjangoFilterBackend, SearchFilter)
    search_fields = ('^first_name', '^last_name')
    filter_class = UserFilter

    def create(self, request, *args, **kwargs):
        request.data['tenant'] = request.user.tenant_id
        super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.tenant = request.user.tenant
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        try:
            super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(data={'detail': 'TOAST.USER_SET_IN_PROJECT'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @list_route(methods=['get'])
    def consultants(self, request):
        group = Group.objects.filter(name=UserRole.TENANT_CONSULTANT_GROUP)
        response = self.filter_groups_and_serialize(group)
        return Response(response)

    @list_route(methods=['get'])
    def collectors(self, request):
        group = Group.objects.filter(name=UserRole.COLLECTOR_GROUP)
        response = self.filter_groups_and_serialize(group)
        return Response(response)

    @list_route(methods=['get'], url_path='tenant-project-managers')
    def tenant_project_managers(self, request):
        group = Group.objects.filter(name=UserRole.TENANT_PROJECT_MANAGER_GROUP)
        response = self.filter_groups_and_serialize(group)
        return Response(response)

    @list_route(methods=['get'], url_path='tenant-product-managers')
    def tenant_product_managers(self, request):
        group = Group.objects.filter(name=UserRole.TENANT_PRODUCT_MANAGER_GROUP)
        response = self.filter_groups_and_serialize(group)
        return Response(response)

    @list_route(methods=['get'], url_path='tenant-users')
    def tenant_users(self, request):
        groups = Group.objects.filter(name__in=UserRole.TENANT_GROUPS)
        response = self.filter_groups_and_serialize(groups)
        return Response(response)

    def filter_groups_and_serialize(self, group):
        queryset = self.filter_queryset(self.queryset).filter(groups__id__in=group).distinct()
        serializer = self.get_serializer_class()(queryset, many=True)
        return serializer.data

    @detail_route(methods=['get'], url_path='detractor-permissions')
    def detractor_permissions(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        return Response(self._filter_company_entities(user.detractors_permissions, user.user_company()))

    @detail_route(methods=['get'], url_path='statistics-permissions')
    def statistics_permissions(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        return Response(self._filter_company_entities(user.statistics_permissions, user.user_company()))

    @detail_route(methods=['get'], url_path='coded-causes-permissions')
    def coded_causes_permissions(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        return Response(self._filter_company_entities(user.coded_causes_permissions, user.user_company()))

    @detail_route(methods=['get'], url_path='management-permissions')
    def management_permissions(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        return Response(self._filter_company_entities(user.management_permissions, user.user_company()))

    def _filter_company_entities(self, permission_method, company):
        company_elements_id = permission_method()
        company_structure = CompanyElementSerializer(company).data
        allowed_company_elements = self.filter_company_and_serialize(company_elements_id)
        company_structure['children'] = FilterCompanyStructure(allowed_company_elements,
                                                               company_elements_id).run_filter()
        return company_structure

    @staticmethod
    def filter_company_and_serialize(company_elements_ids):
        company_elements = CompanyElement.objects.filter(id__in=company_elements_ids)
        serializer = CompanyElementSerializer(company_elements, many=True)
        return serializer.data


class UserPermissionsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A simple ViewSet for viewing all user permissions. Provides 'read-only' actions.
    """
    permission_classes = (IsAuthenticated,)
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer


class UserGroupsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A simple ViewSet for viewing all user groups. Provides 'read-only' actions.
    """
    permission_classes = (IsAuthenticated,)
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    @list_route(methods=['get'], url_path='group-types')
    def groups_types(self, request):
        tenant_groups = self.queryset.filter(name__in=UserRole.TENANT_GROUPS)
        client_groups = self.queryset.filter(name__in=UserRole.CLIENT_GROUPS)
        shopper_groups = self.queryset.filter(name__in=UserRole.SHOPPERS_COLLECTORS)
        result = {
            'tenant': GroupSerializer(tenant_groups, many=True).data,
            'client': GroupSerializer(client_groups, many=True).data,
            'shopper': GroupSerializer(shopper_groups, many=True).data
        }
        return Response(data=result, status=status.HTTP_200_OK)


class PermissionsPerUserViewSet(viewsets.ViewSet):
    """
    View for viewing all permissions for a specific user
    """
    permission_classes = (IsAuthenticated,)

    def list(self, request, user_pk=None):
        queryset = Permission.objects.filter(user=user_pk)
        serializer = PermissionSerializer(queryset, many=True)
        return Response(serializer.data)


class ShopperViewSet(DestroyOneToOneUserMixin, GetSerializerClassMixin, CreateUserMixin, viewsets.ModelViewSet):
    queryset = Shopper.objects.all()
    serializer_class = ShopperSerializer
    serializer_class_get = ShopperSerializerGET
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filter_class = ShopperFilter
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsTenantConsultant),)
    search_fields = ('address',)

    def get_queryset(self):
        return self.queryset.filter(user__tenant=self.request.user.tenant)


class ClientUserViewSet(DestroyOneToOneUserMixin, GetSerializerClassMixin, CreateUserMixin, viewsets.ModelViewSet):
    queryset = ClientUser.objects.select_related('user__tenant', 'company').prefetch_related('user__groups').all()
    serializer_class = ClientUserSerializer
    serializer_class_get = ClientUserSerializerGET
    filter_backends = (DjangoFilterBackend,)
    filter_class = ClientFilter
    filter_fields = ('company',)
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsTenantConsultant),)

    def get_queryset(self):
        return self.queryset.filter(user__tenant=self.request.user.tenant)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        request.data['user']['tenant'] = self.request.user.tenant.id
        serializer = ClientUserSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    @list_route(methods=['get'], url_path='detractors-managers')
    def detractors_managers(self, request):
        queryset = self.filter_queryset(self.queryset)
        managers = queryset.filter(user__groups__name=UserRole.CLIENT_DETRACTORS_MANAGER_GROUP)
        response = self.serializer_class(managers, many=True).data
        return Response(data=response, status=status.HTTP_200_OK)


class CollectorViewSet(viewsets.ModelViewSet):
    queryset = Collector.objects.all()
    serializer_class = CollectorSerializer
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsTenantConsultant),)


class DetractorRespondentForTenantViewSet(viewsets.ModelViewSet):
    queryset = DetractorRespondent.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filter_class = DetractorFilter
    pagination_class = DetractorRespondentPaginator
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsTenantConsultant),)
    serializer_class = DetractorRespondentForTenantSerializer

    def get_queryset(self):
        project = self.request.query_params.get('project')
        queryset = DetractorRespondent.objects.filter(evaluation__project=project)
        return self.serializer_class.setup_eager_loading(queryset)


class DetractorRespondentForClientViewSet(viewsets.ModelViewSet):
    serializer_class = DetractorRespondentForClientSerializer
    queryset = DetractorRespondent.objects.all()
    permission_classes = (IsAuthenticated, HasReadOnlyAccessToProjectsOrEvaluations)
    pagination_class = DetractorRespondentPaginator
    filter_backends = (DetractorFilterPerCompanyElement, DjangoFilterBackend,)
    filter_class = DetractorFilter

    def get_queryset(self):
        queryset = self.serializer_class.setup_eager_loading(self.queryset)
        project = self.request.query_params.get('project')
        return queryset.filter(evaluation__project=project)
