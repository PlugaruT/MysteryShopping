# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedSimpleRouter

from mystery_shopping.users.views import ClientUserViewSet
from mystery_shopping.users.views import UserPermissionsViewSet, UserGroupsViewSet, PermissionsPerUserViewSet

from .views import UserViewSet
from .views import ShopperViewSet
from .views import CollectorViewSet

from mystery_shopping.projects.views import EvaluationPerShopperViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'shoppers', ShopperViewSet)
router.register(r'client-users', ClientUserViewSet)
router.register(r'collectors', CollectorViewSet)
router.register(r'permissions', UserPermissionsViewSet)
router.register(r'groups', UserGroupsViewSet)

user_permissions = NestedSimpleRouter(router, r'users', lookup='user')
user_permissions.register(r'permissions', PermissionsPerUserViewSet, base_name='user-permissions')

shopper_evaluation = NestedSimpleRouter(router, r'shoppers', lookup='shopper')
shopper_evaluation.register(r'evaluations', EvaluationPerShopperViewSet, base_name='shopper-evaluations')
