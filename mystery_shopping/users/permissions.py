# -*- coding: utf-8 -*-
from rest_framework import permissions


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
            if hasattr(request.user, "tenantproductmanager"):
                return True
            return False
        return False


class IsTenantProjectManager(permissions.BasePermission):
    """Permission for TenantProjectManager user.
    """
    def has_permission(self, request, view):
        if request.user:
            if hasattr(request.user, "tenantprojectmanager"):
                return True
            return False
        return False


class IsTenantConsultantViewOnly(permissions.BasePermission):
    """Permission for TenantConsultant user.
    """
    def has_permission(self, request, view):
        if request.user:
            if hasattr(request.user, "tenantconsultant") and request.method in permissions.SAFE_METHODS:
                return True
            return False
        return False


class IsTenantConsultant(permissions.BasePermission):
    """Permission for TenantConsultant user.
    """
    def has_permission(self, request, view):
        if request.user:
            if hasattr(request.user, "tenantconsultant"):
                return True
            return False
        return False


class IsShopper(permissions.BasePermission):
    """Permission for Shopper user.
    """
    def has_permission(self, request, view):
        if request.user:
            if hasattr(request.user, "shopper"):
                return True
            return False
        return False


class HasAccessToEvaluations(permissions.BasePermission):
    """Check if tenant project manager, tenant product manager, tenant consultant or shopper has access to either it's Planned or Accomplished evaluations.
    """
    def has_permission(self, request, view):
        if request.user:
            print(request.user.user_type)
            if request.user.user_type in ['tenantproductmanager', 'tenantprojectmanager', 'tenantconsultant']:
                return True
            return False
        return False


# TODO[iulian] add other permissions as needed.
