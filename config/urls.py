# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django.views import defaults as default_views

from mystery_shopping.common.urls import router as common_router
from mystery_shopping.companies.urls import router as company_router
from mystery_shopping.companies.urls import company_router_for_projects
from mystery_shopping.companies.urls import company_project_router
from mystery_shopping.projects.urls import router as project_router
from mystery_shopping.projects.urls import project_evaluation
from mystery_shopping.questionnaires.urls import router as questionnaire_router
from mystery_shopping.users.urls import router as user_router
from mystery_shopping.users.urls import shopper_router
from mystery_shopping.users.urls import shopper_evaluation


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
    url(r'^api/v1/', include(company_router_for_projects.urls)),
    url(r'^api/v1/', include(company_project_router.urls)),
    url(r'^api/v1/', include(questionnaire_router.urls), name="api"),

    url(r'^api/v1/', include(project_router.urls)),
    url(r'^api/v1/', include(project_evaluation.urls)),
    url(r'^api/v1/', include(user_router.urls)),

    url(r'^api/v1/', include(shopper_router.urls)),
    url(r'^api/v1/', include(shopper_evaluation.urls)),

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
