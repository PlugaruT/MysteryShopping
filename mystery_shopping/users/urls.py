# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import SimpleRouter
from rest_framework_nested.routers import NestedSimpleRouter

from mystery_shopping.users.views import DetractorRespondentViewSet
from . import views

from .views import UserViewSet
from .views import ClientEmployeeViewSet
from .views import ClientManagerViewSet
from .views import ShopperViewSet
from .views import CollectorViewSet
from .views import TenantProductManagerViewSet
from .views import TenantProjectManagerViewSet
from .views import TenantConsultantViewSet
from .views import PersonToAssessViewSet

from mystery_shopping.projects.views import EvaluationPerShopperViewSet


urlpatterns = [
    # URL pattern for the UserListView
    url(
        regex=r'^$',
        view=views.UserListView.as_view(),
        name='list'
    ),

    # URL pattern for the UserRedirectView
    url(
        regex=r'^~redirect/$',
        view=views.UserRedirectView.as_view(),
        name='redirect'
    ),

    # URL pattern for the UserDetailView
    url(
        regex=r'^(?P<username>[\w.@+-]+)/$',
        view=views.UserDetailView.as_view(),
        name='detail'
    ),

    # URL pattern for the UserUpdateView
    url(
        regex=r'^~update/$',
        view=views.UserUpdateView.as_view(),
        name='update'
    ),
]

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'clientemployees', ClientEmployeeViewSet)
router.register(r'clientmanagers', ClientManagerViewSet)
router.register(r'shoppers', ShopperViewSet)
router.register(r'collectors', CollectorViewSet)
router.register(r'tenantproductmanagers', TenantProductManagerViewSet)
router.register(r'tenantprojectmanagers', TenantProjectManagerViewSet)
router.register(r'tenantconsultants', TenantConsultantViewSet)
router.register(r'peopletoassess', PersonToAssessViewSet)
router.register(r'detractors', DetractorRespondentViewSet)

shopper_evaluation = NestedSimpleRouter(router, r'shoppers', lookup='shopper')
shopper_evaluation.register(r'evaluations', EvaluationPerShopperViewSet, base_name='shopper-evaluations')
