# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views import defaults as default_views

from rest_framework_jwt.views import obtain_jwt_token
from rest_framework_jwt.views import refresh_jwt_token

from mystery_shopping.respondents.urls import router as respondents_router
from mystery_shopping.common.urls import router as common_router
from mystery_shopping.companies.urls import router as company_router
from mystery_shopping.companies.urls import company_router_for_projects
from mystery_shopping.companies.urls import company_project_router
from mystery_shopping.projects.urls import router as project_router
from mystery_shopping.projects.urls import project_evaluation
from mystery_shopping.questionnaires.urls import router as questionnaire_router
from mystery_shopping.users.urls import router as user_router
from mystery_shopping.users.urls import user_permissions
from mystery_shopping.users.urls import shopper_evaluation
from mystery_shopping.cxi.urls import router as nps_router
from mystery_shopping.dashboard.urls import router as dashboard_router


urlpatterns = [
    # Django Admin, use {% url 'admin:index' %}
    url(settings.ADMIN_URL, include(admin.site.urls)),

    url(r'^api-token-auth/', obtain_jwt_token),
    url(r'^api-token-refresh/', refresh_jwt_token),

    # User management
    url(r'^accounts/', include('allauth.urls')),

    url(r'^api/v1/common/', include('mystery_shopping.common.urls', namespace='common')),

    url(r'^api/v1/', include('mystery_shopping.cxi.urls', namespace='cxi')),
    url(r'^api/v1/', include('mystery_shopping.companies.urls', namespace='companies')),

    # Your stuff: custom urls includes go here
    url(r'^api/v1/', include(common_router.urls)),

    url(r'^api/v1/', include(company_router.urls)),
    url(r'^api/v1/', include(company_router_for_projects.urls)),
    url(r'^api/v1/', include(company_project_router.urls)),
    url(r'^api/v1/', include(questionnaire_router.urls), name="api"),

    url(r'^api/v1/', include(project_router.urls)),
    url(r'^api/v1/', include(project_evaluation.urls)),
    url(r'^api/v1/', include(user_router.urls)),

    url(r'^api/v1/', include(user_permissions.urls)),
    url(r'^api/v1/', include(shopper_evaluation.urls)),
    url(r'^api/v1/', include(nps_router.urls)),
    url(r'^api/v1/', include(respondents_router.urls)),
    url(r'^api/v1/dashboard/', include(dashboard_router.urls)),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    import debug_toolbar
    urlpatterns += [
        url(r'^400/$', default_views.bad_request),
        url(r'^403/$', default_views.permission_denied),
        url(r'^404/$', default_views.page_not_found),
        url(r'^500/$', default_views.server_error),
        url(r'^__debug__/', include(debug_toolbar.urls))
    ]
