# -*- coding: utf-8 -*-
from rest_framework import permissions
from mystery_shopping.users.roles import UserRole


class IsAccountOwner(permissions.BasePermission):
    """Permission for own user account.
    """
    def has_object_permission(self, request, view, account):
        if request.user:
            return account == request.user
        return False


class IsTenantProductManager(permissions.BasePermission):
    """Permission for TenantProductManager user.
    """
    def has_permission(self, request, view):
        if request.user:
            if hasattr(request.user, UserRole.TENANT_PRODUCT_MANAGER):
                return True
            return False
        return False


class IsTenantProjectManager(permissions.BasePermission):
    """Permission for TenantProjectManager user.
    """
    def has_permission(self, request, view):
        if request.user:
            if hasattr(request.user, UserRole.TENANT_PROJECT_MANAGER):
                return True
            return False
        return False


class IsTenantConsultantViewOnly(permissions.BasePermission):
    """Permission for TenantConsultant user.
    """
    def has_permission(self, request, view):
        if request.user:
            if hasattr(request.user, UserRole.TENANT_CONSULTANT) and request.method in permissions.SAFE_METHODS:
                return True
            return False
        return False


class IsTenantConsultant(permissions.BasePermission):
    """Permission for TenantConsultant user.
    """
    def has_permission(self, request, view):
        if request.user:
            if hasattr(request.user, UserRole.TENANT_CONSULTANT):
                return True
            return False
        return False


class IsShopper(permissions.BasePermission):
    """Permission for Shopper user.
    """
    def has_permission(self, request, view):
        if request.user:
            if hasattr(request.user, UserRole.SHOPPER):
                return True
            return False
        return False


class HasAccessToProjectsOrEvaluations(permissions.BasePermission):
    """Check if tenant project manager, tenant product manager, tenant consultant or shopper has access to either it's Planned or Accomplished evaluations.
    """
    def has_permission(self, request, view):
        if request.user:
            # print(request.user.user_type)
            is_tenant_user = False
            for role in request.user.user_roles:
                if role in UserRole.TENANT_USERS:
                    is_tenant_user = True
            if is_tenant_user:
                return True
            return False
        return False


class HasReadOnlyAccessToProjectsOrEvaluations(permissions.BasePermission):
    """Check if tenant project manager, tenant product manager, tenant consultant or shopper has access to either it's Planned or Accomplished evaluations.
    """
    def has_permission(self, request, view):
        if request.user:
            print(request.user.user_type)
            is_client_user = False
            for role in request.user.user_roles:
                if role in UserRole.CLIENT_USERS:
                    is_client_user = True
            if is_client_user and request.method in permissions.SAFE_METHODS:
                return True
            return False
        return False


class IsShopperAccountOwner(permissions.BasePermission):
    """Permission for own Shopper user account.
    """
    def has_object_permission(self, request, view, shopper):
        if request.user:
            return shopper == request.user.shopper
        return False


class IsCompanyProjectManager(permissions.BasePermission):
    """Permission for TenantProjectManager user.
    """
    def has_permission(self, request, view):
        if request.user:
            if hasattr(request.user, UserRole.CLIENT_PROJECT_MANAGER):
                return True
            return False
        return False



class IsCompanyManager(permissions.BasePermission):
    """Permission for TenantProjectManager user.
    """
    def has_permission(self, request, view):
        if request.user:
            if hasattr(request.user, UserRole.CLIENT_MANAGER):
                return True
            return False
        return False



# TODO[iulian] add other permissions as needed.
