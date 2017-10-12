# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from rest_framework.routers import DefaultRouter

from .views import RespondentForClientViewSet, RespondentForTenantViewSet

router = DefaultRouter()
router.register(r'detractors', RespondentForTenantViewSet)
router.register(r'detractorsforclient', RespondentForClientViewSet, base_name='detractorrespondent-forclient')

