# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from rest_framework.routers import DefaultRouter

from mystery_shopping.respondents.views import RespondentViewSet, RespondentWithCasesViewSet, RespondentCaseViewSet

router = DefaultRouter()
router.register(r'respondents', RespondentViewSet, base_name='respondents')
router.register(r'respondentswithcases', RespondentWithCasesViewSet, base_name='respondentswithcases')
router.register(r'respondentcases', RespondentCaseViewSet, base_name='respondentcases')

