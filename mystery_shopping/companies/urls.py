from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedSimpleRouter
from django.conf.urls import url
from mystery_shopping.companies.views import SubIndustryViewSet, IndustryCsvUploadView, CompanyElementViewSet, \
    AdditionalInfoTypeViewSet
from .views import IndustryViewSet
from .views import CompanyViewSet
from .views import DepartmentViewSet
from .views import EntityViewSet
from .views import SectionViewSet

from mystery_shopping.projects.views import ProjectPerCompanyViewSet

router = DefaultRouter()
router.register(r'industries', IndustryViewSet)
router.register(r'subindustries', SubIndustryViewSet)
router.register(r'departments', DepartmentViewSet)
router.register(r'entities', EntityViewSet)
router.register(r'sections', SectionViewSet)
router.register(r'companies', CompanyViewSet)
router.register(r'company-elements', CompanyElementViewSet)
router.register(r'info-type', AdditionalInfoTypeViewSet)

company_router_for_projects = DefaultRouter()
company_router_for_projects.register(r'company-elements', CompanyElementViewSet, base_name='company-elements')

company_project_router = NestedSimpleRouter(company_router_for_projects, r'company-elements', lookup='company_element')
company_project_router.register(r'projects', ProjectPerCompanyViewSet, base_name='company-element-projects')

urlpatterns = [
    url(r'^upload/industries/$', IndustryCsvUploadView.as_view(), name='upload-industries')
]
