# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import django_filters
from django.core.urlresolvers import reverse
from django.views.generic import DetailView, ListView, RedirectView, UpdateView
from django.db.models import Q

from rest_framework import viewsets
from rest_framework import status
from rest_condition import Or
from braces.views import LoginRequiredMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from mystery_shopping.mystery_shopping_utils.models import TenantFilter
from mystery_shopping.mystery_shopping_utils.paginators import DetractorRespondentPaginator
from mystery_shopping.questionnaires.serializers import DetractorRespondentForTenantSerializer, \
    DetractorRespondentForClientSerializer
from mystery_shopping.users.models import DetractorRespondent
from .models import ClientEmployee
from .models import ClientManager
from .models import Shopper
from .models import Collector
from .models import TenantProjectManager
from .models import TenantProductManager
from .models import TenantConsultant
from .models import User
from .models import PersonToAssess

from .serializers import UserSerializer
from .serializers import ClientEmployeeSerializer
from .serializers import ClientManagerSerializer
from .serializers import ShopperSerializer
from .serializers import CollectorSerializer
from .serializers import TenantProductManagerSerializer
from .serializers import TenantProjectManagerSerializer
from .serializers import TenantConsultantSerializer
from .serializers import PersonToAssessSerializer
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

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (TenantFilter,)


class TenantProductManagerViewSet(FilterQuerysetOnTenantMixIn, viewsets.ModelViewSet):
    queryset = TenantProductManager.objects.all()
    serializer_class = TenantProductManagerSerializer


class TenantProjectManagerViewSet(FilterQuerysetOnTenantMixIn, viewsets.ModelViewSet):
    queryset = TenantProjectManager.objects.all()
    serializer_class = TenantProjectManagerSerializer


class TenantConsultantViewSet(FilterQuerysetOnTenantMixIn, viewsets.ModelViewSet):
    queryset = TenantConsultant.objects.all()
    serializer_class = TenantConsultantSerializer


class ClientEmployeeViewSet(FilterQuerysetOnTenantMixIn,  viewsets.ModelViewSet):
    queryset = ClientEmployee.objects.all()
    serializer_class = ClientEmployeeSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.has_evaluations():
            return Response({"You can not delete this object because there are evaluations applied"},
                            status.HTTP_400_BAD_REQUEST)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ClientManagerViewSet(FilterQuerysetOnTenantMixIn, viewsets.ModelViewSet):
    queryset = ClientManager.objects.all()
    serializer_class = ClientManagerSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.has_evaluations():
            return Response({"You can not delete this object because there are evaluations applied"},
                            status.HTTP_400_BAD_REQUEST)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShopperViewSet(viewsets.ModelViewSet):
    queryset = Shopper.objects.all()
    serializer_class = ShopperSerializer
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsTenantConsultant),)

    def get_queryset(self):
        """Filter the Shoppers by tenant (if they belong to the request.tenant or have no tenant)
        """
        queryset = self.queryset.all()
        queryset = queryset.filter(Q(tenant__isnull=True) | Q(tenant=self.request.user.tenant))
        return queryset

    def list(self, request, *args, **kwargs):
        project_type = self.request.query_params.get('type', 'm')
        if project_type == 'm':
            queryset = self.get_queryset().filter(is_collector=False)
        elif project_type == 'c':
            queryset = self.get_queryset().filter(is_collector=True)

        serializer = ShopperSerializer(queryset, many=True)
        return Response(serializer.data)


class CollectorViewSet(viewsets.ModelViewSet):
    queryset = Collector.objects.all()
    serializer_class = CollectorSerializer
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsTenantConsultant),)


class PersonToAssessViewSet(viewsets.ModelViewSet):
    queryset = PersonToAssess.objects.all()
    serializer_class = PersonToAssessSerializer


class DetractorFilter(django_filters.rest_framework.FilterSet):
    entity = django_filters.AllValuesMultipleFilter(name="evaluation__entity")
    date = django_filters.DateFilter(name="evaluation__time_accomplished", lookup_expr='date')

    class Meta:
        model = DetractorRespondent
        fields = ['entity', 'date']


class DetractorRespondentForTenantViewSet(viewsets.ModelViewSet):
    queryset = DetractorRespondent.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filter_class = DetractorFilter
    pagination_class = DetractorRespondentPaginator
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsTenantConsultant),)
    serializer_class = DetractorRespondentForTenantSerializer

    def get_queryset(self):
        queryset = self.get_serializer_class().setup_eager_loading(self.queryset)
        project = self.request.query_params.get('project')
        return queryset.filter(evaluation__project=project)


class DetractorRespondentForClientViewSet(viewsets.ModelViewSet):
    serializer_class = DetractorRespondentForClientSerializer
    queryset = DetractorRespondent.objects.all()
    permission_classes = (IsAuthenticated, HasReadOnlyAccessToProjectsOrEvaluations)
    pagination_class = DetractorRespondentPaginator
    filter_backends = (DjangoFilterBackend,)
    filter_class = DetractorFilter

    # TODO: Update this method
    def get_queryset(self):
        queryset = self.get_serializer_class().setup_eager_loading(self.queryset)
        project = self.request.query_params.get('project')
        list_of_places = [place['place_id'] for place in self.request.user.list_of_poses]
        if isinstance(self.request.user.user_type_attr, ClientManager):
            return queryset.filter(evaluation__project=project, evaluation__entity__in=list_of_places)
        return queryset.filter(evaluation__project=project)
