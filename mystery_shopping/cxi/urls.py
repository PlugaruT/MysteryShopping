from django.conf.urls import patterns
from django.conf.urls import include
from django.conf.urls import url

from rest_framework.routers import DefaultRouter

from .views import CodedCauseLabelViewSet
from .views import CodedCauseViewSet
from .views import ProjectCommentViewSet
from .views import OverviewDashboard
from .views import IndicatorDashboard
from .views import IndicatorDashboardList


router = DefaultRouter()
router.register(r'codedcauselabels', CodedCauseLabelViewSet)
router.register(r'codedcauses', CodedCauseViewSet)
router.register(r'projectcomments', ProjectCommentViewSet)

urlpatterns = [
    url(r'^cxi/overview/$',
        OverviewDashboard.as_view(),
        name='overview-score'),
    url(r'^cxi/indicator/$',
        IndicatorDashboard.as_view(),
        name='indicator-score'),
    url(r'^cxi/indicatorlist/$',
        IndicatorDashboardList.as_view(),
        name='indicator-list'),
]