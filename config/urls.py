# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django.views import defaults as default_views

from rest_framework.routers import DefaultRouter

from mystery_shopping.questionnaires.views import QuestionnaireScriptViewSet, QuestionnaireTemplateViewSet, \
    QuestionnaireTemplateBlockViewSet, QuestionnaireTemplateQuestionViewSet
from mystery_shopping.companies.views import CompanyViewSet, DepartmentViewSet, EntityViewSet, SectionViewSet
from mystery_shopping.projects.views import ProjectViewSet


questionnaire_router = DefaultRouter()
questionnaire_router.register(r'scripts', QuestionnaireScriptViewSet)
questionnaire_router.register(r'templatequestionnaires', QuestionnaireTemplateViewSet)
questionnaire_router.register(r'templateblocks', QuestionnaireTemplateBlockViewSet)
questionnaire_router.register(r'questions', QuestionnaireTemplateQuestionViewSet)

company_router = DefaultRouter()
company_router.register(r'companies', CompanyViewSet)
company_router.register(r'departments', DepartmentViewSet)
company_router.register(r'entities', EntityViewSet)
company_router.register(r'sections', SectionViewSet)

project_router = DefaultRouter()
project_router.register(r'projects', ProjectViewSet)

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='pages/home.html'), name="home"),
    url(r'^about/$', TemplateView.as_view(template_name='pages/about.html'), name="about"),

    # Django Admin, use {% url 'admin:index' %}
    url(settings.ADMIN_URL, include(admin.site.urls)),

    # User management
    url(r'^users/', include("mystery_shopping.users.urls", namespace="users")),
    url(r'^accounts/', include('allauth.urls')),

    # Your stuff: custom urls includes go here

    url(r'^api/questionnaires/', include(questionnaire_router.urls), name="api"),
    url(r'^api/clients/', include(company_router.urls)),
    url(r'^api/projects/', include(project_router.urls)),

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
