# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django.views import defaults as default_views

from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from mystery_shopping.common.views import CountryViewSet
from mystery_shopping.common.views import CountryRegionViewSet
from mystery_shopping.common.views import CountyViewSet
from mystery_shopping.common.views import CityViewSet
from mystery_shopping.common.views import SectorViewSet

from mystery_shopping.companies.views import IndustryViewSet
from mystery_shopping.companies.views import CompanyViewSet
from mystery_shopping.companies.views import DepartmentViewSet
from mystery_shopping.companies.views import EntityViewSet
from mystery_shopping.companies.views import SectionViewSet

from mystery_shopping.questionnaires.views import QuestionnaireScriptViewSet
from mystery_shopping.questionnaires.views import QuestionnaireViewSet
from mystery_shopping.questionnaires.views import QuestionnaireTemplateViewSet
from mystery_shopping.questionnaires.views import QuestionnaireTemplateBlockViewSet
from mystery_shopping.questionnaires.views import QuestionnaireBlockViewSet
from mystery_shopping.questionnaires.views import QuestionnaireQuestionViewSet
from mystery_shopping.questionnaires.views import QuestionnaireTemplateQuestionViewSet

from mystery_shopping.projects.views import ProjectViewSet
from mystery_shopping.projects.views import ResearchMethodologyViewSet
from mystery_shopping.projects.views import PlannedEvaluationViewSet
from mystery_shopping.projects.views import PlannedEvaluationPerShopperViewSet
from mystery_shopping.projects.views import AccomplishedEvaluationViewSet
from mystery_shopping.projects.views import AccomplishedEvaluationPerShopperViewSet

from mystery_shopping.users.views import UserViewSet
from mystery_shopping.users.views import ClientEmployeeViewSet
from mystery_shopping.users.views import ClientManagerViewSet
from mystery_shopping.users.views import ProjectWorkerViewSet
from mystery_shopping.users.views import ShopperViewSet
from mystery_shopping.users.views import TenantProductManagerViewSet
from mystery_shopping.users.views import TenantProjectManagerViewSet


common_router = DefaultRouter()
common_router.register(r'countries', CountryViewSet)
common_router.register(r'countryregions', CountryRegionViewSet)
common_router.register(r'counties', CountyViewSet)
common_router.register(r'cities', CityViewSet)
common_router.register(r'sectors', SectorViewSet)

company_router = DefaultRouter()
company_router.register(r'industries', IndustryViewSet)
company_router.register(r'companies', CompanyViewSet)
company_router.register(r'departments', DepartmentViewSet)
company_router.register(r'entities', EntityViewSet)
company_router.register(r'sections', SectionViewSet)

questionnaire_router = DefaultRouter()
questionnaire_router.register(r'scripts', QuestionnaireScriptViewSet)
questionnaire_router.register(r'questionnaires', QuestionnaireViewSet)
questionnaire_router.register(r'templatequestionnaires', QuestionnaireTemplateViewSet)
questionnaire_router.register(r'blocks', QuestionnaireBlockViewSet)
questionnaire_router.register(r'templateblocks', QuestionnaireTemplateBlockViewSet)
questionnaire_router.register(r'questions', QuestionnaireQuestionViewSet)
questionnaire_router.register(r'templatequestions', QuestionnaireTemplateQuestionViewSet)

project_router = DefaultRouter()
project_router.register(r'projects', ProjectViewSet)
project_router.register(r'researchmethodologies', ResearchMethodologyViewSet)
project_router.register(r'plannedevaluations', PlannedEvaluationViewSet)
project_router.register(r'accomplishedevaluations', AccomplishedEvaluationViewSet)

users_router = DefaultRouter()
users_router.register(r'users', UserViewSet)
users_router.register(r'clientemployees', ClientEmployeeViewSet)
users_router.register(r'clientmanagers', ClientManagerViewSet)
users_router.register(r'projectworkers', ProjectWorkerViewSet)
# users_router.register(r'shoppers', ShopperViewSet)
users_router.register(r'tenantproductmanagers', TenantProductManagerViewSet)
users_router.register(r'tenantprojectmanagers', TenantProjectManagerViewSet)


shopper_router = routers.SimpleRouter()
shopper_router.register(r'shoppers', ShopperViewSet)

shopper_planned_evaluation = routers.NestedSimpleRouter(shopper_router, r'shoppers', lookup='shopper')
shopper_planned_evaluation.register(r'plannedevaluations', PlannedEvaluationPerShopperViewSet, base_name='shopper-planned-evaluations')

shopper_accomplished_evaluation = routers.NestedSimpleRouter(shopper_router, r'shoppers', lookup='shopper')
shopper_accomplished_evaluation.register(r'accomplishedevaluations', AccomplishedEvaluationPerShopperViewSet, base_name='shopper-accomplished-evaluations')


urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='pages/home.html'), name="home"),
    url(r'^about/$', TemplateView.as_view(template_name='pages/about.html'), name="about"),

    # Django Admin, use {% url 'admin:index' %}
    url(settings.ADMIN_URL, include(admin.site.urls)),

    url(r'^api-token-auth/', 'rest_framework_jwt.views.obtain_jwt_token'),
    url(r'^api-token-refresh/', 'rest_framework_jwt.views.refresh_jwt_token'),

    # User management
    url(r'^users/', include("mystery_shopping.users.urls", namespace="users")),
    url(r'^accounts/', include('allauth.urls')),

    # Your stuff: custom urls includes go here
    url(r'^api/v1/', include(common_router.urls)),

    url(r'^api/v1/', include(company_router.urls)),
    url(r'^api/v1/', include(questionnaire_router.urls), name="api"),

    url(r'^api/v1/', include(project_router.urls)),
    url(r'^api/v1/', include(users_router.urls)),

    url(r'^api/v1/', include(shopper_router.urls)),
    url(r'^api/v1/', include(shopper_planned_evaluation.urls)),
    url(r'^api/v1/', include(shopper_accomplished_evaluation.urls)),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        url(r'^400/$', default_views.bad_request),
        url(r'^403/$', default_views.permission_denied),
        url(r'^404/$', default_views.page_not_found),
        url(r'^500/$', default_views.server_error),
    ]
