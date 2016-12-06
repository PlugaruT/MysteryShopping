from django.conf.urls import url

from rest_framework.routers import DefaultRouter

from mystery_shopping.cxi.views import FrustrationWhyCauseViewSet, AppreciationWhyCauseViewSet
from .views import CxiIndicatorTimelapse
from .views import WhyCauseViewSet
from .views import CodedCausePercentage
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
router.register(r'whycauses', WhyCauseViewSet)
router.register(r'frustration-whycauses', FrustrationWhyCauseViewSet)
router.register(r'appreciation-whycauses', AppreciationWhyCauseViewSet)

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
    url(r'^cxi/indicatortimelapse/$',
        CxiIndicatorTimelapse.as_view(),
        name='indicator-timestamp'),
    url(r'^cxi/codedcausepercentage',
        CodedCausePercentage.as_view(),
        name='codedcause-percentage')
]
