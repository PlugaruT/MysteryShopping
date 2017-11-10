# -*- coding: utf-8 -*-
from rest_framework import permissions
from mystery_shopping.users.roles import UserRole


class IsAccountOwner(permissions.BasePermission):
    """
        Permission for own user account.
    """

    def has_object_permission(self, request, view, account):
        if request.user:
            return account == request.user
        return False


class IsTenantProductManager(permissions.BasePermission):
    """
        Permission for TenantProductManager user.
    """

    def has_permission(self, request, view):
        if request.user:
            if request.user.is_in_group(UserRole.TENANT_PRODUCT_MANAGER_GROUP):
                return True
            return False
        return False


class IsTenantProjectManager(permissions.BasePermission):
    """
        Permission for TenantProjectManager user.
    """

    def has_permission(self, request, view):
        if request.user:
            if request.user.is_in_group(UserRole.TENANT_PROJECT_MANAGER_GROUP):
                return True
            return False
        return False


class IsTenantConsultantViewOnly(permissions.BasePermission):
    """
        Permission for TenantConsultant user.
    """

    def has_permission(self, request, view):
        if request.user:
            if request.user.is_in_group(
                UserRole.TENANT_CONSULTANT_GROUP) and request.method in permissions.SAFE_METHODS:
                return True
            return False
        return False


class IsTenantConsultant(permissions.BasePermission):
    """
        Permission for TenantConsultant user.
    """

    def has_permission(self, request, view):
        if request.user:
            if request.user.is_in_group(UserRole.TENANT_CONSULTANT_GROUP):
                return True
            return False
        return False


class IsDetractorManager(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user:
            return request.user.is_in_group(UserRole.CLIENT_DETRACTORS_MANAGER_GROUP)
        return False


class IsShopper(permissions.BasePermission):
    """
        Permission for Shopper user.
    """

    def has_permission(self, request, view):
        if request.user:
            if request.user.is_in_group(UserRole.SHOPPER_GROUP):
                return True
            return False
        return False


class IsCollector(permissions.BasePermission):
    """
        Permission for Collector user.
    """

    def has_permission(self, request, view):
        if request.user:
            if request.user.is_in_group(UserRole.COLLECTOR_GROUP):
                return True
            return False
        return False


class HasAccessToProjectsOrEvaluations(permissions.BasePermission):
    """
        Check if tenant project manager, tenant product manager, tenant consultant or shopper
        has access to either it's Planned or Accomplished evaluations.
    """

    def has_permission(self, request, view):
        if request.user:
            is_tenant_user = False
            for group in request.user.get_group_names():
                if group in UserRole.TENANT_GROUPS:
                    is_tenant_user = True
            if is_tenant_user:
                return True
            return False
        return False


class HasReadOnlyAccessToProjectsOrEvaluations(permissions.BasePermission):
    """
        Check if tenant project manager, tenant product manager, tenant consultant or shopper
        has access to either it's Planned or Accomplished evaluations.
    """

    def has_permission(self, request, view):
        if request.user:
            is_client_user = False
            for group in request.user.get_group_names():
                if group in UserRole.CLIENT_GROUPS:
                    is_client_user = True
            if is_client_user and request.method in permissions.SAFE_METHODS:
                return True
            return False
        return False


class IsShopperAccountOwner(permissions.BasePermission):
    """
        Permission for own Shopper user account.
    """

    def has_object_permission(self, request, view, shopper):
        if request.user:
            return shopper == request.user.shopper
        return False


class IsCompanyProjectManager(permissions.BasePermission):
    """
        Permission for TenantProjectManager user.
    """

    def has_permission(self, request, view):
        if request.user:
            if request.user.is_in_group(UserRole.CLIENT_PROJECT_MANAGER_GROUP):
                return True
            return False
        return False


class IsCompanyManager(permissions.BasePermission):
    """
        Permission for TenantProjectManager user.
    """

    def has_permission(self, request, view):
        if request.user:
            if request.user.is_in_group(UserRole.CLIENT_MANAGER_GROUP):
                return True
            return False
        return False


class IsCompanyEmployee(permissions.BasePermission):
    """
        Permission for Company Employee user.
    """

    def has_permission(self, request, view):
        if request.user:
            if request.user.is_in_group(UserRole.CLIENT_EMPLOYEE_GROUP):
                return True
            return False
        return False


class HasAccessToDashboard(permissions.BasePermission):
    """
        Permission for users that should have access to dashboard
    """

    def has_permission(self, request, view):
        if request.user:
            possible_groups = UserRole.TENANT_GROUPS + UserRole.CLIENT_GROUPS
            return request.user.is_in_groups(possible_groups)
        return False
