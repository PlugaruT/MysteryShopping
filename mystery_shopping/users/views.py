# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import json

from django.core.urlresolvers import reverse
from django.views.generic import DetailView, ListView, RedirectView, UpdateView
from django.db.models import Q

from rest_framework import viewsets
from rest_framework import status
from rest_condition import Or
from braces.views import LoginRequiredMixin
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response

from .models import ClientEmployee
from .models import ClientManager
from .models import Shopper
from .models import Collector
from .models import TenantProjectManager
from .models import TenantProductManager
from .models import TenantConsultant
from .models import User
from .models import PersonToAssess
from mystery_shopping.users.services import ShopperService

from .serializers import UserSerializer
from .serializers import ClientEmployeeSerializer
from .serializers import ClientManagerSerializer
from .serializers import ShopperSerializer
from .serializers import CollectorSerializer
from .serializers import TenantProductManagerSerializer
from .serializers import TenantProjectManagerSerializer
from .serializers import TenantConsultantSerializer
from .serializers import PersonToAssessSerializer
from mystery_shopping.users.permissions import IsTenantProductManager, IsShopperAccountOwner
from mystery_shopping.users.permissions import IsTenantProjectManager
from mystery_shopping.users.permissions import IsTenantConsultant


class FilterQuerysetOnTenantMixIn:
    """
    Mixin class that adds 'get_queryset' that filters the queryset agains the request.user.tenant
    """
    def get_queryset(self):
        queryset = self.queryset
        queryset = queryset.filter(tenant=self.request.user.tenant)
        return queryset


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    # These next two lines tell the view to index lookups by username
    slug_field = "username"
    slug_url_kwarg = "username"

    # TODO: permission classes for editing profile
    # authentificated, istenant__, isshopper..


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse("users:detail",
                       kwargs={"username": self.request.user.username})


class UserUpdateView(LoginRequiredMixin, UpdateView):

    fields = ['name', ]

    # we already imported User in the view code above, remember?
    model = User

    # send the user back to their own page after a successful update
    def get_success_url(self):
        return reverse("users:detail",
                       kwargs={"username": self.request.user.username})

    def get_object(self):
        # Only get the User record for the user making the request
        return User.objects.get(username=self.request.user.username)


class UserListView(LoginRequiredMixin, ListView):
    model = User
    # These next two lines tell the view to index lookups by username
    slug_field = "username"
    slug_url_kwarg = "username"


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class TenantProductManagerViewSet(FilterQuerysetOnTenantMixIn,viewsets.ModelViewSet):
    queryset = TenantProductManager.objects.all()
    serializer_class = TenantProductManagerSerializer


class TenantProjectManagerViewSet(FilterQuerysetOnTenantMixIn,viewsets.ModelViewSet):
    queryset = TenantProjectManager.objects.all()
    serializer_class = TenantProjectManagerSerializer


class TenantConsultantViewSet(FilterQuerysetOnTenantMixIn,viewsets.ModelViewSet):
    queryset = TenantConsultant.objects.all()
    serializer_class = TenantConsultantSerializer


class ClientEmployeeViewSet(FilterQuerysetOnTenantMixIn,viewsets.ModelViewSet):
    queryset = ClientEmployee.objects.all()
    serializer_class = ClientEmployeeSerializer


class ClientManagerViewSet(FilterQuerysetOnTenantMixIn,viewsets.ModelViewSet):
    queryset = ClientManager.objects.all()
    serializer_class = ClientManagerSerializer


class ShopperViewSet(viewsets.ModelViewSet):
    queryset = Shopper.objects.all()
    serializer_class = ShopperSerializer
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsTenantConsultant),)

    def get_queryset(self):
        """Filter the Shoppers by tenant (if they belong to the request.tenant or have no tenant)
        """
        queryset = self.queryset
        queryset = queryset.filter(Q(tenant__isnull=True) | Q(tenant=self.request.user.tenant))
        return queryset

    @detail_route(permission_classes=(IsShopperAccountOwner,))
    def imacollector(self, request, *args, **kwargs):
        """A view to return a list of entities paired up with their corresponding
        questionnaires.

        The view serves calls from Customer Experience Index project and returns the
        list of available entities with all the required information to fill in a
        questionnaire and create a realized evaluation.

        :returns: List of ids and serialized objects.
        :rtype: list
        """
        shopper_service = ShopperService(request.user.shopper)
        available_list_of_places = shopper_service.get_available_list_of_places_with_questionnaires()

        return Response(available_list_of_places, status=status.HTTP_200_OK)


class CollectorViewSet(viewsets.ModelViewSet):
    queryset = Collector.objects.all()
    serializer_class = CollectorSerializer
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsTenantConsultant),)


class PersonToAssessViewSet(FilterQuerysetOnTenantMixIn,viewsets.ModelViewSet):
    queryset = PersonToAssess.objects.all()
    serializer_class = PersonToAssessSerializer

