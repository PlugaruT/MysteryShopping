# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedSimpleRouter

from mystery_shopping.users.views import DetractorRespondentForTenantViewSet, DetractorRespondentForClientViewSet
from mystery_shopping.users.views import DetractorRespondentForTenantViewSet, DetractorRespondentForClientViewSet, \
    UserPermissionsViewSet, UserGroupsViewSet, PermissionsPerUserViewSet
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
router.register(r'detractors', DetractorRespondentForTenantViewSet)
router.register(r'detractorsforclient', DetractorRespondentForClientViewSet)
router.register(r'permissions', UserPermissionsViewSet)
router.register(r'groups', UserGroupsViewSet)

user_permissions = NestedSimpleRouter(router, r'users', lookup='user')
user_permissions.register(r'permissions', PermissionsPerUserViewSet, base_name='user-permissions')

shopper_evaluation = NestedSimpleRouter(router, r'shoppers', lookup='shopper')
shopper_evaluation.register(r'evaluations', EvaluationPerShopperViewSet, base_name='shopper-evaluations')
