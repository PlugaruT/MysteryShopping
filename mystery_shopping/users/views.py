# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.core.urlresolvers import reverse
from django.views.generic import DetailView, ListView, RedirectView, UpdateView
from rest_framework import viewsets

from braces.views import LoginRequiredMixin

from .models import User
from .models import ProjectWorker
from .models import Shopper
from .models import TenantProjectManager
from .serializers import ProjectWorkerSerializer
from .serializers import ShopperSerializer
from .serializers import TenantProjectManagerSerializer


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    # These next two lines tell the view to index lookups by username
    slug_field = "username"
    slug_url_kwarg = "username"


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


class TenantProjectManagerViewSet(viewsets.ModelViewSet):
    queryset = TenantProjectManager.objects.all()
    serializer_class = TenantProjectManagerSerializer


class ShopperViewSet(viewsets.ModelViewSet):
    queryset = Shopper.objects.all()
    serializer_class = ShopperSerializer


class ProjectWorkerViewSet(viewsets.ModelViewSet):
    queryset = ProjectWorker.objects.all()
    serializer_class = ProjectWorkerSerializer

