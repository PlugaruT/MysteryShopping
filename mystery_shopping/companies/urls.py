from django.conf.urls import url
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedSimpleRouter

from mystery_shopping.companies.views import (
    AdditionalInfoTypeViewSet,
    CompanyElementViewSet,
    IndustryCsvUploadView,
    IndustryViewSet,
    SubIndustryViewSet
)
from mystery_shopping.projects.views import ProjectPerCompanyViewSet

router = DefaultRouter()
router.register(r'industries', IndustryViewSet)
router.register(r'subindustries', SubIndustryViewSet)
router.register(r'company-elements', CompanyElementViewSet)
router.register(r'info-type', AdditionalInfoTypeViewSet)

company_router_for_projects = DefaultRouter()
company_router_for_projects.register(r'company-elements', CompanyElementViewSet, base_name='company-elements')

company_project_router = NestedSimpleRouter(company_router_for_projects, r'company-elements', lookup='company_element')
company_project_router.register(r'projects', ProjectPerCompanyViewSet, base_name='company-element-projects')

app_name = 'companies'

urlpatterns = [
    url(r'^upload/industries/$', IndustryCsvUploadView.as_view(), name='upload-industries')
]
