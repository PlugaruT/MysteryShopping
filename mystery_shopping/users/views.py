# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import django_filters
from django.contrib.auth.models import Permission, Group
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework import status
from rest_condition import Or
from rest_framework.decorators import list_route, detail_route
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from mystery_shopping.companies.models import CompanyElement
from mystery_shopping.companies.serializers import CompanyElementSerializer
from mystery_shopping.mystery_shopping_utils.models import TenantFilter
from mystery_shopping.mystery_shopping_utils.paginators import DetractorRespondentPaginator
from mystery_shopping.mystery_shopping_utils.permissions import DetractorFilterPerCompanyElement
from mystery_shopping.mystery_shopping_utils.views import GetSerializerClassMixin
from mystery_shopping.questionnaires.serializers import DetractorRespondentForTenantSerializer, \
    DetractorRespondentForClientSerializer
from mystery_shopping.users.models import DetractorRespondent, ClientUser
from mystery_shopping.users.roles import UserRole
from mystery_shopping.users.serializers import PermissionSerializer, GroupSerializer, UserSerializerGET, \
    ClientUserSerializer, ShopperSerializerGET, ClientUserSerializerGET
from .models import Shopper
from .models import Collector
from .models import User

from .serializers import UserSerializer
from .serializers import ShopperSerializer
from .serializers import CollectorSerializer
from mystery_shopping.users.permissions import IsTenantProductManager, HasReadOnlyAccessToProjectsOrEvaluations
from mystery_shopping.users.permissions import IsTenantProjectManager
from mystery_shopping.users.permissions import IsTenantConsultant


# Todo: remove this
class FilterQuerysetOnTenantMixIn:
    """
    Mixin class that adds 'get_queryset' that filters the queryset agains the request.user.tenant
    """

    def get_queryset(self):
        queryset = self.queryset.all()
        queryset = queryset.filter(tenant=self.request.user.tenant)
        return queryset


class CreateUserMixin:
    def create(self, request, *args, **kwargs):
        request.data['user']['tenant'] = request.user.tenant.id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class UserFilter(django_filters.rest_framework.FilterSet):
    groups = django_filters.AllValuesMultipleFilter(name="groups")

    class Meta:
        model = User
        fields = ['groups', ]


class UserViewSet(GetSerializerClassMixin, viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    serializer_class_get = UserSerializerGET
    filter_backends = (TenantFilter, DjangoFilterBackend,)
    filter_class = UserFilter

    def create(self, request, *args, **kwargs):
        request.data['tenant'] = request.user.tenant_id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.tenant = request.user.tenant
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @list_route(methods=['get'])
    def consultants(self, request):
        group = Group.objects.filter(name=UserRole.TENANT_CONSULTANT_GROUP)
        response = self.filter_and_serialize(group)
        return Response(response)

    @list_route(methods=['get'])
    def collectors(self, request):
        group = Group.objects.filter(name=UserRole.COLLECTOR_GROUP)
        response = self.filter_and_serialize(group)
        return Response(response)

    @list_route(methods=['get'], url_path='tenant-project-managers')
    def tenant_project_managers(self, request):
        group = Group.objects.filter(name=UserRole.TENANT_PROJECT_MANAGER_GROUP)
        response = self.filter_and_serialize(group)
        return Response(response)

    @list_route(methods=['get'], url_path='tenant-product-managers')
    def tenant_product_managers(self, request):
        group = Group.objects.filter(name=UserRole.TENANT_PRODUCT_MANAGER_GROUP)
        response = self.filter_and_serialize(group)
        return Response(response)

    @list_route(methods=['get'], url_path='tenant-users')
    def tenant_users(self, request):
        groups = Group.objects.filter(name__in=UserRole.TENANT_GROUPS)
        response = self.filter_and_serialize(groups)
        return Response(response)

    @list_route(methods=['get'], url_path='client-users')
    def client_users(self, request):
        groups = Group.objects.filter(name__in=UserRole.CLIENT_GROUPS)
        response = self.filter_and_serialize(groups)
        return Response(response)

    def filter_and_serialize(self, group):
        queryset = self.filter_queryset(self.queryset).filter(groups__id__in=group).distinct()
        serializer = self.get_serializer_class()(queryset, many=True)
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
        tenant_groups = Group.objects.filter(name__in=UserRole.TENANT_GROUPS)
        client_groups = Group.objects.filter(name__in=UserRole.CLIENT_GROUPS)
        shopper_groups = Group.objects.filter(name__in=UserRole.SHOPPERS_COLLECTORS)
        result = [
            {
                'type': 'tenant',
                'groups': GroupSerializer(tenant_groups, many=True).data
            },
            {
                'type': 'client',
                'groups': GroupSerializer(client_groups, many=True).data
            },
            {
                'type': 'shopper',
                'groups': GroupSerializer(shopper_groups, many=True).data
            }
        ]
        return Response(result)


class PermissionsPerUserViewSet(viewsets.ViewSet):
    """
    View for viewing all permissions for a specific user
    """
    permission_classes = (IsAuthenticated,)

    def list(self, request, user_pk=None):
        queryset = Permission.objects.filter(user=user_pk)
        serializer = PermissionSerializer(queryset, many=True)
        return Response(serializer.data)


class ShopperFilter(django_filters.rest_framework.FilterSet):
    license = django_filters.BooleanFilter(name='has_drivers_license')
    sex = django_filters.CharFilter(name='user__gender')
    age = django_filters.DateFromToRangeFilter(name='user__date_of_birth')

    class Meta:
        model = Shopper
        fields = ['license', 'sex', 'age']


class ShopperViewSet(GetSerializerClassMixin, CreateUserMixin, viewsets.ModelViewSet):
    queryset = Shopper.objects.all()
    serializer_class = ShopperSerializer
    serializer_class_get = ShopperSerializerGET
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filter_class = ShopperFilter
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsTenantConsultant),)
    search_fields = ('address',)

    def get_queryset(self):
        return self.queryset.filter(user__tenant=self.request.user.tenant)


class ClientFilter(django_filters.rest_framework.FilterSet):
    groups = django_filters.AllValuesMultipleFilter(name="user__groups")

    class Meta:
        model = ClientUser
        fields = ['groups', 'company']


class ClientUserViewSet(GetSerializerClassMixin, CreateUserMixin, viewsets.ModelViewSet):
    queryset = ClientUser.objects.all()
    serializer_class = ClientUserSerializer
    serializer_class_get = ClientUserSerializerGET
    filter_backends = (DjangoFilterBackend,)
    filter_class = ClientFilter
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

    @detail_route(methods=['get'], url_path='detractor-permissions')
    def detractor_permissions(self, request, pk=None):
        client_user = get_object_or_404(ClientUser, pk=pk)
        company_elements = client_user.user.detractors_permissions()
        response = self.filter_and_serialize(company_elements)
        return Response(response)

    @detail_route(methods=['get'], url_path='statistics-permissions')
    def statistics_permissions(self, request, pk=None):
        client_user = get_object_or_404(ClientUser, pk=pk)
        company_elements = client_user.user.statistics_permissions()
        response = self.filter_and_serialize(company_elements)
        return Response(response)

    @detail_route(methods=['get'], url_path='coded-causes-permissions')
    def coded_causes_permissions(self, request, pk=None):
        client_user = get_object_or_404(ClientUser, pk=pk)
        company_elements = client_user.user.coded_causes_permissions()
        response = self.filter_and_serialize(company_elements)
        return Response(response)

    @detail_route(methods=['get'], url_path='management-permissions')
    def management_permissions(self, request, pk=None):
        client_user = get_object_or_404(ClientUser, pk=pk)
        company_elements = client_user.user.management_permissions()
        response = self.filter_and_serialize(company_elements)
        return Response(response)

    @staticmethod
    def filter_and_serialize(company_elements_ids):
        company_elements = CompanyElement.objects.filter(id__in=company_elements_ids)
        serializer = CompanyElementSerializer(company_elements, many=True)
        return serializer.data


class CollectorViewSet(viewsets.ModelViewSet):
    queryset = Collector.objects.all()
    serializer_class = CollectorSerializer
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsTenantConsultant),)


class DetractorFilter(django_filters.rest_framework.FilterSet):
    place = django_filters.AllValuesMultipleFilter(name="evaluation__company_element")
    date = django_filters.DateFilter(name="evaluation__time_accomplished", lookup_expr='date')
    questions = django_filters.NumberFilter(name='number_of_questions')

    class Meta:
        model = DetractorRespondent
        fields = ['date', 'place', 'status', 'questions']


class DetractorRespondentForTenantViewSet(viewsets.ModelViewSet):
    queryset = DetractorRespondent.objects.all()
    filter_backends = (DetractorFilterPerCompanyElement, DjangoFilterBackend,)
    filter_class = DetractorFilter
    pagination_class = DetractorRespondentPaginator
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsTenantConsultant),)
    serializer_class = DetractorRespondentForTenantSerializer

    def get_queryset(self):
        queryset = self.serializer_class.setup_eager_loading(self.queryset)
        project = self.request.query_params.get('project')
        return queryset.filter(evaluation__project=project)


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
