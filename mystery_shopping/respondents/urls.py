# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from mystery_shopping.respondents.views import AverageTimePerState, RespondentCaseViewSet, RespondentCasesPerIssueTag, \
    RespondentCasesPerSolutionTag, RespondentCasesPerState, RespondentCasesPerUser, RespondentViewSet, \
    RespondentWithCasesViewSet, RespondentsDistribution

router = DefaultRouter()
router.register(r'respondents', RespondentViewSet, base_name='respondents')
router.register(r'respondentswithcases', RespondentWithCasesViewSet, base_name='respondentswithcases')
router.register(r'respondentcases', RespondentCaseViewSet, base_name='respondentcases')

app_name = 'respondents'

urlpatterns = [
    url(r'^respondents/distribution', RespondentsDistribution.as_view(), name='distribution'),
    url(r'^respondents/cases-per-state', RespondentCasesPerState.as_view(), name='cases-per-state'),
    url(r'^respondents/cases-per-solution-tag', RespondentCasesPerSolutionTag.as_view(), name='cases-per-solution-tag'),
    url(r'^respondents/cases-per-issue-tag', RespondentCasesPerIssueTag.as_view(), name='cases-per-issue-tag'),
    url(r'^respondents/cases-per-user', RespondentCasesPerUser.as_view(), name='cases-per-user'),
    url(r'^respondents/time-per-state', AverageTimePerState.as_view(), name='time-per-state'),
]
