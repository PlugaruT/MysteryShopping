# -*- coding: utf-8 -*-
from rest_framework import permissions


class IsAccountOwner(permissions.BasePermission):
    """Permission for own user account.
    """
    def has_object_permission(self, request, view, account):
        if request.user:
            return account == request.user
        return False


class TenantProductManager(permissions.BasePermission):
    """Permission for TenantProductManager user.
    """
    def has_permission(self, request, view):
        if request.user:
            if request.user.tenantproductmanager:
                return True
            return False
        return False


# TODO[iulian] add other permissions as needed.
