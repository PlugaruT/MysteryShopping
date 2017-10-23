# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from rest_framework.routers import DefaultRouter

from .views import RespondentForClientViewSet, RespondentForTenantViewSet

respondents_router = DefaultRouter()
respondents_router.register(r'detractors', RespondentForTenantViewSet)
respondents_router.register(r'detractorsforclient', RespondentForClientViewSet,
                            base_name='detractorrespondent-forclient')
