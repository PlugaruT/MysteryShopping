from guardian.shortcuts import get_objects_for_user
from rest_framework import permissions
from rest_framework.filters import BaseFilterBackend

from mystery_shopping.companies.models import CompanyElement


class MysteryObjectPermissions(permissions.DjangoObjectPermissions):
    """
    Similar to `DjangoObjectPermissions`, but adding 'view' permissions.
    """
    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': ['%(app_label)s.view_%(model_name)s'],
        'HEAD': ['%(app_label)s.view_%(model_name)s'],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }


class DetractorFilterPerCompanyElement(BaseFilterBackend):
    """
    Filter class that will check for which company elements the user has
    permissions to view detractors
    """

    def filter_queryset(self, request, queryset, view):
        company_elements = get_objects_for_user(request.user, klass=CompanyElement,
                                                perms=['view_detractors_for_companyelement']).values_list('id',
                                                                                                          flat=True)
        return queryset.filter(evaluation__company_element__in=company_elements)


class ProjectStatisticsFilterPerCompanyElement(BaseFilterBackend):
    """
    Filter class that will check for which company elements the user has
    permissions to view project statistics
    """

    def filter_queryset(self, request, queryset, view):
        company_elements = get_objects_for_user(request.user, klass=CompanyElement,
                                                perms=['view_statistics_for_companyelement']).values_list('id',
                                                                                                          flat=True)
        return queryset.filter(company_element__in=company_elements)
